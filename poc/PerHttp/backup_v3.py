#!/usr/bin/env python
# -*- coding: utf-8 -*-
# @Time    : 19/12/2 14:13
# @Author  : Chaos
# @File    : backup_v3.py

import requests
from itertools import product
from queue import Queue
import threading
import re
from lib.loader import notice
from urllib.parse import urlparse

def plugin_info():
	plugin_info = {
			"level":"Medium",
	        "category":"备份文件",
	        "extra":"备份文件",
		    "info":"备份文件泄露"
	        }
	return plugin_info

def gen(url):
	parse = urlparse(url)
	filename = ["rar", "zip", "tar.gz", "tar.gtar", "tar", "tgz", "tar.bz", "tar.bz2", "bz", "bz2", "boz", "3gp", "gz2", "sql", "7z"]
	rule1 = ["web", "webroot", "WebRoot", "website", "bin", "bbs", "shop", "www", "wwww", "db", "logo",
				'1', '2', '3', '4', '5', '6', '7', '8', '9', '10', '11',
				"www1", "www2", "www3", "www4", "default", "log", "logo", "kibana", "elk", "weblog", "data", "backup",
				"mysql", "ftp", "FTP", "MySQL", "redis", "Redis",
				"cgi", "php", "jsp",
				"access", "error", "logs", "other_vhosts_access",
				"database", "sql",
			]
	target = ['.'.join(p) for p in product(rule1, filename)]
	domain = parse.netloc
	if not re.search(r"\A\d{1,3}\.\d{1,3}\.\d{1,3}\.\d{1,3}\Z", url):
		if ':' in domain:
			url1 = 'www.' + domain.split(":")[0]
			url2 = domain.split(":")[0]
		else:
			url1 = 'www.' + domain
			url2 = domain
		p = ['.'.join(p) for p in product([url1, url2], filename)]
		# print(p)
		target += p
		return target

def scan(url, file):
	try:
		if "http://" not in url:
			url = 'http://' +  url
		targeturl = url.strip('/') + '/' + file
		# print(targeturl)

		#sys.stdout.write('[+] Checking %s' % targeturl)
		#sys.stdout.flush()
		c = requests.head(targeturl, timeout=3, allow_redirects=False, stream=True)
		if c.status_code == 200 and "octet-stream" in c.headers["Content-Type"]:
			# print ("[Backup leak]: " + targeturl)
			#notice("Backup Leak {}".format(targeturl))
			return targeturl, False
	except Exception:
		pass
	return False, False



def worker(url,q):
	while not q.empty():
		port = q.get()
		try:
			scan(url, port)
		finally:
			q.task_done()

def poc(hostname, port, service):
	if service.lower().find('http') < 0:
		return False, False
	url = '%s://%s:%s' % (service, hostname, port)
	q = Queue()
	for i in gen(url): q.put(i)
	for i in range(20):
		t = threading.Thread(target=worker, args=(url,q))
		t.start()

