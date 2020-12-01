#!/usr/bin/env python
# -*- coding: utf-8 -*-
# @Time    : 20/1/6 14:41
# @Author  : Chaos
# @File    : tasks.py

import json
import datetime
import re
import sys
import os
import socket
sys.path.append(os.path.dirname(os.path.dirname(__file__)))
from plugin.BBScan.bbscan import check_white_list, Web, check_black_list
from lib.DBPool import redis_conn
from lib.log import log
from lib.common import get_hostname_port, http_request, decode_text, get_host_ip, check_http_status, http_detect
from lib.mongo import db
from lib.checkCDN import is_cdn


from celery import Celery
app = Celery('tasks', broker="redis://127.0.0.1:6379/6", backend='redis://127.0.0.1:6379/7')


@app.task(name="tasks.before_scan")
def scan_init(task_name, task_id, target, tag_name):
	"""
	3个模块的初始化判断
	1. 去除多余的空格
	2. 校验是不是IP或者域名
	3. 域名是否可以解析IP, IP是否可以连通
	4. 如果可以连通，然后判断是否开启了端口扫描，可以的话进入到端口扫描流程
	5. 判断运行的service
	6. 根据运行的service，如果是http的话，进入到bbscan
	7. 获取运行的service，进入到poc扫描,因为POC扫描只有两种service可识别，所以只需要判断是否是http服务就可以了。
	:return:
	"""

	target = target.strip()
	scheme, host, port = get_hostname_port(target)
	target = '%s://%s:%s' % (scheme, host, port)
	ips, hostname = get_host_ip(target)  #获取hostname和ip地址
	if ips:
		ip = ips[0]
	else:
		return
	iscdn = is_cdn(ip)
	if len(ips) > 1:
		log.info("Multi ip: %s", ips)
	if iscdn:
		db.portInfo.update_one({"task_id":task_id, "task_name":task_name},{"$set": {"url": hostname,"cdn": true}})
		log.info("CDN Check True: %s", target)


	ports = list(db.task.find({"task_id":task_id},{"_id":0,"ports":1}))[0]['ports']
	if ports and not iscdn:
		_ = {
			"task_name": task_name,
			"task_id": task_id,
			"tag_name": tag_name,
			"ip": ip,
			"hostname": hostname,
			"ports": ports
		}
		log.info("Task Port Scan Begin %s", hostname)
		redis_conn.lpush("Task_Port_Scan", json.dumps(_))

	# service = None
	# alive = None
	s = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
	s.settimeout(5.0)
	try:
		if s.connect_ex((host, int(port))) == 0:
			log.info("Port Open %s:%s", host, port)

			if port == 443:
				target = 'https://{}'.format(hostname)
				service = 'https'
			elif port == 80:
				target = 'http://{}'.format(hostname)
				service = 'http'
			else:
				service, content = http_detect(host, port)  # 端口开放的时候，判断运行的是什么服务，用来丢给POC扫描流程
				if service == 'http':
					if 'The plain HTTP request was sent to HTTPS port' in content:
						service = 'https'
			status_code, headers, content = http_request(target)
			if status_code in (301, 302) and headers['Location']:
				_ = {
					"task_name": task_name,
					"task_id": task_id,
					"target": headers['Location'],
					"tag_name": tag_name
					}
				log.info("Http %s redirect to %s", target, headers['Location'])
				redis_conn.lpush("before_scan", json.dumps(_))


			alive = True
			# content =  content.eocode()  if content is isinstance(content, str) else content
			if check_white_list(content):   # 白名单储存到数据库
				log.error("White List Check True")
				db.bbscan.update_one({"task_id":task_id,"task_name":task_name,"tag_name":tag_name},
				                     {"$set":{"vul_Type": "white list", "url": target}})
				# return
# 			if service in ('http', 'https'): # http端口保存到资产数据库
# 				m = re.search('<title>(.*?)</title>', content)
# 				title = m.group(1) if m else ''
# 				db.portInfo.update_one({"task_id": task_id, "task_name": task_name,"tag_name":tag_name, "ip":ip, "port":port},
# 				                       {"$set":{"server": service,"banner": content,"title":title,"hostname":hostname,"url":target}},upsert=True)

		else:
			log.info("Port Closed %s:%s", host, port)
			service = False
			alive = False
	except Exception:
		log.error('[Warning] Fail to connect to %s:%s' % (host, port), exc_info=True)
		return
	finally:
		s.close()

	pocs = list(db.task.find({"task_id":task_id},{"_id":0,"pocs":1}))[0]['pocs']

	if alive:  # 主机是否存活
		log.info("host %s is alive, Check Scan options", target)
		if pocs and service:  # service表示是否开启运行了http还是unknown
			log.info("Begin POC Scan %s", target)
			_ = {
				"task_name": task_name,
				"task_id": task_id,
				"hostname": host,
				"port": port,
				"pocs": pocs,
				"tag_name": tag_name,
				"service": service
			}
			redis_conn.lpush("Task_Poc_Scan", json.dumps(_))



		elif list(db.task.find({"task_id":task_id},{"_id":0,"BBScan_flag":1}))[0]['BBScan_flag'] and service in ('http', 'https'):
			_ = {
				"task_name": task_name,
				"task_id": task_id,
				"target": target,
				"tag_name": tag_name
			}
			redis_conn.lpush("BBScan_init", json.dumps(_))
		else:
			log.info("[Warning]: No POC Selected: %s", target)
			pass


@app.task(name="tasks.spider_init")
def spider_init(task_name, task_id, target, tag_name):
	try:
		scheme, host, port = get_hostname_port(target)
		# if check_port_open(host, port):  # 检测端口连通性
		# 	log.info("Check port is Open: %s:%s", host, port)
		check_http_status(scheme, host, port, task_name, task_id, tag_name)
		# else:
		# 	log.info("Check port is Close: %s:%s", host, port)
	except:
		log.error("Spider_init Exception", exc_info=True)
	# 	check_http_status(scheme, host, port,task_name, task_id) # 检查http服务的状态

@app.task(name='tasks.spider_first')
def bbscan_parse_uri(scheme, ip, port, title, content, status_code, header, task_name, task_id, tag_name):
	"""
	检查是否在白名单-> 从content解析二级路径-> 把路径和要检测的内容组合成新的url
	检测白名单放在后面，更具有通用性
	:param content:
	:return:
	"""
	try:
		if check_white_list(content):
			data = {"ip":ip, "port":port, "vul_title":title}
			redis_conn.lpush("VulScan", json.dumps(data))  # TODO 存储BBScan白名单的结果到数据库
			# return
		else:
			log.info("starting parse uri for %s://%s:%s", scheme,ip,port)
			web = Web(scheme, ip, port, title, content, status_code, header, task_name, task_id, tag_name)
			web.init_run()
	except:
		log.error("celery task parse_uri error for %s://%s:%s", scheme,ip,port, exc_info=True)


@app.task(name='tasks.spider_second')
def bbscan(url, tag, status_to_match, content_type, content_type_no, vul_type, status_404, len_404_content, task_name, task_id, tag_name):
	status_to_match = int(status_to_match)
	status_404 = int(status_404)
	try:
		status_code, headers, content = http_request(url)
		cur_content_type = headers['Content-Type']
		status = status_code
		content = decode_text(content)
		cur_content_length = len(content)
		if check_black_list(content):  # 在黑名单的的url返回
			return
		if 0 <= int(cur_content_length) <= 10:  # text too short
			return
		if cur_content_type.find('image/') >= 0:  # exclude image
			return
		if content_type != 'application/json' and cur_content_type.find('application/json') >= 0 and \
				not url.endswith('.json'):   # invalid json
			return
		if content_type and cur_content_type.find(content_type) < 0 \
				or content_type_no and cur_content_type.find(content_type_no) >= 0:
			return  # content type mismatch
		if tag and content.find(tag) < 0:
			return  # tag mismatch
		if check_white_list(content):
			valid_item = True
		else:
			if status_to_match == 206 and status != 206:
				return
			if status_to_match in (200, 206) and status in (200, 206):
				valid_item =True
			elif status_to_match and status != status_to_match:
				return
			elif status in (403, 404) and status != status_to_match:
				return
			else:
				valid_item =True

			if status == status_404 and url != '/':
				len_doc = len(content)
				len_sum = int(len_404_content) + len_doc
				# print("bool is %s" % bool(0.4 <= float(len_doc) / len_sum <= 0.6))
				if len_sum == 0 or (0.4 <= float(len_doc) / len_sum <= 0.6):
					return

		if valid_item:
			vul_type = vul_type.replace('_',' ')
			m =  re.search('<title>(.*?)</title>', content)
			title = m.group(1) if m else ''
			scheme, host, port = get_hostname_port(url)
			vul_url = "%s://%s:%s" % (scheme, host, port)
			first_find_date = datetime.datetime.now().strftime("%Y-%m-%d %H:%M:%S")
			# log.info(bool(db.bbscan.find_one({"task_id": task_id, "url": url})))
			if db.bbscan.find_one({"task_id": task_id, "tag_name":tag_name, "vul_url": url}): # 以task_id和url为主键查询条件
				log.info("Get Vul Repeat %s", {"task_id": task_id, "url": url})
				db.bbscan.update({"task_id": task_id, "url": url}, {"$set": {"last_find_date": first_find_date}})
			else:
				log.info("Get Vul Success %s", {"task_id": task_id, "url": url})
				result = {"task_name": task_name, "task_id": task_id,"tag_name": tag_name,"vul_url":url,"url": vul_url,"vul_Type": vul_type, "status": status, "title": title,
				          "first_find_date": first_find_date, "last_find_date": first_find_date}
				db.bbscan.insert(result)

	except TypeError:
		pass
	except KeyError:
		pass
	except:
		log.error("BBScan::process_request error %s", url, exc_info=True)
