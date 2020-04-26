#!/usr/bin/env python
# -*- coding: utf-8 -*-
# @Time    : 19/12/19 15:21
# @Author  : Chaos
# @File    : subscribe.py


"""
准备数据，保存数据到redis里面
检测redis队列的数据，然后执行celery任务，作为调度中心的角色。
"""
import time
from plugin.BBScan.bbscan import *
from plugin.tasks import bbscan_parse_uri, bbscan, spider_init, scan_init
from celerynode.tasks import  vuln_scan,masscan_scan, nmap_scan
from lib.DBPool import redis_conn
from lib.log import log
from lib.mongo import db
import os
import sys




def store_poc():
	"""
	定时扫描目录下的POC，更新POC的信息到DB
	:return:
	"""
	root_path = os.path.abspath(os.path.dirname(__file__))
	poc_path = root_path + '/poc/'
	for root, dirs, files in os.walk(poc_path):
		for file in files:
			# print(file)
			if file.split('.')[-1] == 'py':
				sys.path.append(root)
				statinfo = os.stat(root + '/' + file)
				mtime = datetime.datetime.fromtimestamp(statinfo.st_mtime).strftime("%Y-%m-%d %H:%M:%S")
				module = __import__(file.split('.')[0])
				try:
					plugin_info = module.plugin_info()
				except AttributeError:
					plugin_info = {}
				if db.plugin.find_one({"poc":file}):  # 更新POC插件信息
					db.plugin.update_one({"poc":file}, {"$set": dict({"mtime": mtime}, **plugin_info)})
				else:
					db.plugin.insert_one(dict({"folder": os.path.basename(root),"poc": file, "mtime": mtime}, **plugin_info))

# store_poc()

def before_scan():
	while redis_conn.llen("before_scan"):
		task_unit = json.loads(redis_conn.lpop("before_scan"))
		task_id = task_unit['task_id']
		task_name = task_unit['task_name']
		target = task_unit['target']
		tag_name = task_unit['tag_name']
		scan_init.delay(task_name, task_id, target, tag_name)


def scheduler_poc_scan():
	while redis_conn.llen("Task_Poc_Scan"):
		poc_object = json.loads(redis_conn.lpop("Task_Poc_Scan"))
		task_name = poc_object["task_name"]
		task_id = poc_object["task_id"]
		tag_name = poc_object["tag_name"]
		hostname = poc_object["hostname"]
		port = poc_object["port"]
		pocs = poc_object["pocs"]
		pocs = pocs.split(',') if isinstance(pocs, str) else pocs
		service = poc_object['service']
		# service = poc_object['service'] or 'http'
		# log.info("subscribe: pocs is %s:%s" % (pocs, type(pocs)))
		#
		# try:
		# 	service = poc_object['service']
		# except:
		# 	service = 'http'
		log.info('target is %s service is %s' % (hostname + ':' + str(port), service))
		if service and pocs:  # 识别出来的服务，比如http，https
			for poc in pocs:
				vuln_scan.delay(hostname, port, service, poc, task_id, task_name, tag_name)

def scheduler_port_scan_first():
	while redis_conn.llen("Task_Port_Scan"):
		port_object = json.loads(redis_conn.lpop('Task_Port_Scan'))
		task_name = port_object["task_name"]
		task_id = port_object["task_id"]
		tag_name = port_object["tag_name"]
		hostname = port_object["hostname"]
		ip = port_object["ip"]
		ports = port_object["ports"]
		if ports:  # 设置了端口之后，对端口进行扫描
			# chain(masscan_scan.s(target, task_name, task_id, ports) | nmap_scan.s()).apply_async()
			masscan_scan.delay(hostname, ip, task_name, task_id, ports, tag_name)

def scheduler_port_scan_second():
	while redis_conn.llen("Nmap_Second"):
		port_object = json.loads(redis_conn.lpop("Nmap_Second"))
		hostname = port_object['hostname']
		ip = port_object['ip']
		tag_name = port_object['tag_name']
		ports = port_object['ports']
		task_name = port_object['task_name']
		task_id = port_object['task_id']
		if ports:
			nmap_scan.delay(hostname, ip, ports, task_name, task_id, tag_name)

def scheduler_bbscan_scan_init():
	while redis_conn.llen("BBScan_init"):
		_ = json.loads(redis_conn.lpop("BBScan_init"))
		task_name = _["task_name"]
		task_id = _["task_id"]
		target = _["target"]
		tag_name = _["tag_name"]
		spider_init.delay(task_name, task_id, target, tag_name)


def scheduler_bbscan_scan_first():
	while redis_conn.llen("BBScan_First"):
		try:
			http_object = json.loads(redis_conn.lpop("BBScan_First"))  # 获取第一步待扫描的内容
			scheme = http_object['scheme']
			ip = http_object['ip']
			port = http_object['port']
			header = http_object['banner'].split("\r\n\r\n\r\n")[0]
			content = http_object['banner'].split("\r\n\r\n\r\n")[1]
			status_code = http_object['status_code']
			task_name = http_object['task_name']
			task_id = http_object['task_id']
			tag_name = http_object['tag_name']

			m = re.search('<title>(.*?)</title>', content)
			title = m.group(1) if m else ''
			bbscan_parse_uri.delay(scheme, ip, port, title, content, status_code, header, task_name, task_id, tag_name)
		except:
			log.error("scheduler_bbscan_scan_first", exc_info=True)
		# print("Ret is %s" % ret)
		# if not ret:
		# 	continue

def scheduler_bbscan_scan_second():
	while redis_conn_byte.llen("BBScan_Second"):
		l = redis_conn_byte.lpop("BBScan_Second").decode('utf-8').split(',')
		url, tag, status_to_match, content_type, content_type_no, vul_type, status_404, len_404_content, \
		task_name, task_id, tag_name= l
		bbscan.delay(url, tag, status_to_match, content_type, content_type_no, vul_type, status_404, len_404_content,
		             task_name, task_id, tag_name)

init_rules()  # save rules to redis
save_black_white()  # save white_and_black list to redis
store_poc()  # POC扫描存储

while True:
	try:
		before_scan()
		scheduler_poc_scan()  # POC扫描
		scheduler_port_scan_first()  # 端口扫描
		scheduler_port_scan_second()
		scheduler_bbscan_scan_init()
		scheduler_bbscan_scan_first() #BBScan第一步扫描
		scheduler_bbscan_scan_second() # BBScan第二步扫描
	except Exception as e:
		time.sleep(10)
		print(str(e))
		pass

