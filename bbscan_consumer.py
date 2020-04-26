#!/usr/bin/env python
# -*- coding: utf-8 -*-
# @Time    : 20/3/9 17:48
# @Author  : Chaos
# @File    : bbscan_consumer.py
import time
from plugin.BBScan.bbscan import *
from plugin.tasks import  bbscan


def scheduler_bbscan_scan_second():
	while redis_conn_byte.llen("BBScan_Second"):
		l = redis_conn_byte.lpop("BBScan_Second").decode('utf-8').split(',')
		url, tag, status_to_match, content_type, content_type_no, vul_type, status_404, len_404_content, task_name, task_id = l
		# print(l)
		# print("scan %s" % url)
		bbscan.delay(url, tag, status_to_match, content_type, content_type_no, vul_type, status_404, len_404_content,
		             task_name, task_id)

while True:
	try:
		scheduler_bbscan_scan_second()
	except Exception as e:
		print(str(e))
		time.sleep(10)