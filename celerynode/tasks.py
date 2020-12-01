#!/usr/bin/env python
# -*- coding: utf-8 -*-
# @Time    : 19/11/6 16:38
# @Author  : Chaos
# @File    : tasks.py

import os
import sys
import subprocess
import re
import nmap
import requests
import urllib3
urllib3.disable_warnings(urllib3.exceptions.InsecureRequestWarning)
import json

sys.path.append(os.path.dirname(os.path.dirname(__file__)))
from lib.loader import  *
from lib.DBPool import *
from lib.common import decode_text, http_detect, get_http_desc
from lib.port_fingerprint import fingerprint_scan
from settings import MASSCAN
from lib.mongo import db


from celery import Celery
app = Celery('tasks', broker="redis://127.0.0.1:6379/2", backend='redis://127.0.0.1:6379/3')
# app.config_from_object(CeleryConfig)
# app.conf.beat_schedule = {
# 	#任务名称自定义可随意
# 	'service_redis_consumer': {
# 		'task': 'tasks.service_scan',#任务所在路径且指定哪个任务
# 		'schedule': crontab(seconds=3,minute=0),  #定时任务相关
# 	},
# }



@app.task(name='tasks.vuln_scan')
def vuln_scan(hostname, port, service, poc, task_id, task_name, tag_name):
	"""
	:param url 要扫描的URL
	:param poc 需要扫描的poc
	"""
	if poc.find(".py") < 0:
		poc += ".py"
	log.info("target host is %s and port is %s, service is %s" % (hostname, port, service))
	obj = load_code_to_obj(poc)
	result, response = None, None
	try:
		result, response = obj.poc(hostname, port, service)
	except Exception:
		log.error("[Error]: POC Processing Error")
	if result:
		vul_info = obj.plugin_info()
		if response:
			if not isinstance(response, str):
				response = decode_text(response)
		response = response if response else " "
		vul_level = vul_info['level'] if vul_info else None  # 漏洞等级
		vul_type = vul_info['category'] if vul_info else None  # 漏洞类型
		vul_name = vul_info['info'] if vul_info else None  # 漏洞描述
		first_find_date = datetime.datetime.now().strftime("%Y-%m-%d %H:%M:%S")
		query = {'url': hostname, 'port': port, 'poc': poc, 'task_id': task_id, 'tag_name': tag_name}
		# print(query)
		if db.vulBlack.find_one({"vul_url": result,"poc":poc}):
			log.error("Vul in Black List, ignore: %s", result)
			return
		if db.vulPoc.find_one(query):
			log.info("Vul exist, Update Find Date")
			db.vulPoc.update(query, {"$set":{"last_find_date": first_find_date}})  #如果已存在记录，更新最新发现时间
		else:
			payload = {'task_id':task_id,'task_name': task_name, 'tag_name': tag_name,'name':vul_name, 'level':vul_level, 'type':vul_type,
			           'vul_url':result,'vul_response':response,
			           'vul_desc':' ','black_flag': 0,'first_find_date':first_find_date, 'last_find_date': first_find_date}
			db.vulPoc.insert(dict(query, **payload))
			log.info("find Vul %s, %s",hostname + ':' +str(port), poc)
			#以下是把漏洞内容推送到redis，最后到es，需要测试是否存在线程不安全的问题
			# tags = {"tags": "vulScan"}
			# rdata = dict(query, **payload, **tags)
			# redis_conn.lpush("vulScan", json.dumps(rdata))

			# message = "Vuln: {}: {}".format(hostname + ':' +port, poc)
			# notice(message) 发送钉钉通知消息，到最后充分测试完成之后打开



@app.task(name='tasks.masscan_scan')
def masscan_scan(hostname, ip, task_name, task_id, ports, tag_name):
	"""
	masscan扫描端口，获取开放的端口
	:param url:
	:return: str "22,80" 开放的端口列表
	"""
	args = [MASSCAN.PATH, '-p', ports, '--rate', MASSCAN.RATE, ip]
	try:
		p = subprocess.Popen(args,stdin=subprocess.PIPE,
            stdout=subprocess.PIPE,
            stderr=subprocess.PIPE)
		output, error = p.communicate()
		if  output:
			pattern = re.compile(r"port (\d+)/")
			match = re.findall(pattern, decode_text(output))
		elif "Permission denied" in decode_text(error):
			log.error("You Must Use Root To Run Masscan", exc_info=True)
			sys.exit(0)
		else:
			match = None
	except Exception:
		log.error("Masscan Scan Ports Failed", exc_info=True)
		match = None

	log.info("Masscan Success: %s: %s",ip, match)
	nmap_object = {
		"task_id": task_id,
		"task_name": task_name,
		"tag_name": tag_name,
		"hostname": hostname,
		"ip": ip,
		"ports": match
	}
	redis_conn.lpush("Nmap_Second", json.dumps(nmap_object))


@app.task(name='tasks.nmap_scan')
def nmap_scan(hostname, ip, ports,task_name, task_id, tag_name):
	"""
	nmap扫描获取服务，端口从masscan的结果得出
	使用delay的时候，第二次再扫描会出现端口filtered的情况，另外443的https会被判断为http
	:param args:
	:return:
	"""
	log.info('nmap processing: IP: %s, Port: %s', ip, ports)
	if not (ip and ports):
		log.error("nmap Failed for %s, ip or port is none", ip, exc_info=True)
		return
	ports = ",".join(ports[:20])  #只扫描20个端口
	ip = ip
	try:

		nm = nmap.PortScanner()
		nm.scan(ip, ports=ports, arguments="-Pn -n -sT -sV")
		log.info("get nmap result %s", nm[ip])
		if "tcp" in nm[ip].all_protocols():
			for port in nm[ip]["tcp"].keys():
				# if nm[ip]["tcp"][port]["state"] == "open":
				if nm[ip]["tcp"][port]["state"]:
					# nm[host]["tcp"][port]["extrainfo"] match codes
					# pattern = re.compile('(php)|(aspx?)|(jsp)|(python)', re.I)
					# match = pattern.search(nm[ip]["tcp"][port]["extrainfo"])
					# if match:
					# 	codes = match.group().lower()
					# else:
					# 	codes = ""
					log.info("Get fingerprint for %s:%s",ip, port)
# 					server = fingerprint_scan(ip, port)  #判断设备指纹
					server, _ = http_detect(ip, port)  #判断是http服务还是非http服务
					server = server if server != 'unknown' else nm[ip]["tcp"][port]["name"]

					title, status_code, banner = None, None, None
					if server in ('http', 'https'):
						_ = '%s://%s:%s' %  (server, ip, port)
						title, banner, status_code = get_http_desc(_)

					# status_code = None
					# if not server:
					# 	title, scheme, banner, status_code = try_web(ip, port)
					# 	if not scheme:
					# 		title, scheme, banner, status_code = try_https(ip, port)
					# 	server = scheme if scheme else nm[ip]["tcp"][port]["name"]
					# 	server = server if server else 'unknown'

					result = {
						"server": server,
						"status_code": status_code,
						"title": title,
						"banner": banner,
						"url": hostname,
						"product": nm[ip]["tcp"][port]["product"],
						"state": nm[ip]["tcp"][port]["state"],
						"version": nm[ip]["tcp"][port]["version"],
						"extrainfo": nm[ip]["tcp"][port]["extrainfo"],
						"cpe": nm[ip]["tcp"][port]["cpe"],
						"first_find_date": datetime.datetime.now().strftime("%Y-%m-%d %H:%M:%S"),
						"last_find_date": datetime.datetime.now().strftime("%Y-%m-%d %H:%M:%S")
					}
					# print('nmap final result for %s:%s is %s' % (ip, port, result))
					condition = {'task_name': task_name,'task_id': task_id, 'tag_name': tag_name,'ip': ip, 'port': port}
					log.info("Store Ports Scan Result To DB %s", condition)

					#TODO 页面相似性判断，如果差别比较大，更新banner，反之不变
# 					if db.portInfo.find_one(condition):
# 						db.portInfo.update(condition, {"last_find_date":
# 							                               datetime.datetime.now().strftime("%Y-%m-%d %H:%M:%S")})
# 						log.info("--------Update Success---------\n%s", condition)
# 					else:
					db.portInfo.insert(dict(condition, **result))
					log.info("\n--------Store Success---------%s")

					pocs = list(db.task.find({"task_id": task_id},{"pocs": 1, "_id":0}))[0]['pocs'] #任务ID对应的POC
					poc_task = {
						'task_id': task_id,
						'task_name': task_name,
						'tag_name': tag_name,
						'pocs': pocs,
						'hostname': hostname,
						'port': port,
						'service': server
					}
					if pocs:
						redis_conn.lpush("Task_Poc_Scan", json.dumps(poc_task))


					BBScan_flag = list(db.task.find({"task_id": task_id},{"BBScan_flag": 1, "_id":0}))[0]["BBScan_flag"]
					if server in ['http', 'https'] and BBScan_flag:  #存储数据到redis，后续bbscan消费使用
						rdata = {'scheme': server, 'port': port, 'ip': ip, 'title': title, 'status_code': status_code,
						         "banner": banner, 'task_name': task_name, 'task_id': task_id, 'tag_name': tag_name}
						redis_conn.lpush("BBScan_First", json.dumps(rdata))

	except Exception:
		log.error("nmap scan failed for %s:%s", ip, ports, exc_info=True)
