#!/usr/bin/env python
# -*- coding: utf-8 -*-
# @Time    : 19/11/8 16:39
# @Author  : Chaos
# @File    : gitleak.py

import requests

req_timeout = 3

def plugin_info():
	plugin_info = {
			"level":"Medium",
	        "category":"敏感信息泄露",
	        "extra":"git_and_svn",
		    "info":"GIT, SVN, DS_STORE泄露"
	        }
	return plugin_info

def poc(hostname, port, service):
	if service.lower().find('http') < 0:
		return False, False
	# if '://' not in url:
	url = '%s://%s:%s' % (service, hostname, port)
	dsUrl = url.rstrip('/') + "/.DS_store"
	gitUrl = url.rstrip('/') + "/.git/config"
	svnUrl = url.rstrip('/') + "/.svn/entries"
	# print dsUrl
	try:

		c = requests.get(dsUrl, timeout=req_timeout, allow_redirects=False, stream=True)
		r = c.raw.read(10).hex()

		if r == "00000001427564310000" and c.status_code == 200:
			return dsUrl, c.content

		c = requests.get(gitUrl, timeout=req_timeout).text
		if '[remote "origin"]' in c:
			# ret = {
			# 	'algroup': 'Git Index Leak',
			# 	'affects': gitUrl,
			# 	'details': 'Git Index Leak'
			# }
			return gitUrl,  c
		c = requests.get(svnUrl, timeout=req_timeout, allow_redirects=False, stream=True)
		if c.raw.read(5).hex() == '31300a0a64':
			return svnUrl,  c.content
	except Exception as e:
		print(str(e))
		# pass
	return False, False

# print(poc("127.0.0.1", 80, 'http'))