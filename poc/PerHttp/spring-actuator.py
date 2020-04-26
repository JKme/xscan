#!/usr/bin/env python
# -*- coding: utf-8 -*-
# @Time    : 19/12/2 14:10
# @Author  : Chaos
# @File    : spring-actuator.py
import requests


req_timeout = 3
def plugin_info():
	plugin_info = {
			"level":"Low",
	        "category":"信息泄露",
	        "extra":"",
		    "info": "spring调试模式打开"
	        }
	return plugin_info
def poc(hostname, port, service):
	if service.lower().find('http') < 0:
		return False, False
	url = '%s://%s:%s' % (service, hostname, port)
	targeturl1 = url.rstrip('/') + "/error"
	targeturl2 = url.rstrip('/') + "/env"
	try:
		c1 = requests.get(targeturl1,verify=False)
		c2 = requests.get(targeturl2,verify=False)
		if c1.status_code == 500 and '"status":999' in c1.content.decode('utf-8') and 'spring' in c2.content.decode('utf-8'):
			return url, False
	except Exception:
		# raise e
		pass
	return False, False