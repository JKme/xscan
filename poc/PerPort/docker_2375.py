#!/usr/bin/env python
# -*- coding: utf-8 -*-
# @Time    : 20/3/16 16:18
# @Author  : Chaos
# @File    : docker_2375.py

import requests

req_timeout = 3
def plugin_info():
	plugin_info = {
			"level":"High",
	        "category":"远程命令执行",
	        "extra":"",
		    "info": "远程命令执行"
	        }
	return plugin_info


def poc(hostname, port, service):
	if service.lower().find('http') < 0:
		return False, False
	url = '%s://%s:%s/containers/json' % (service, hostname, port)

	try:
		c1 = requests.get(url,verify=False)
		if 'HostConfig' in c1.content.decode('utf-8'):
			return True, False
	except Exception:
		pass
	return False, False