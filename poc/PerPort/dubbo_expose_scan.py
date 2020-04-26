#!/usr/bin/env python
# -*- coding: utf-8 -*-
# @Time    : 20/3/11 10:23
# @Author  : Chaos
# @File    : dubbo_expose_scan.py.py

import socket
import time


def plugin_info():
	plugin_info = {
			"level":"Medium",
	        "category":"信息泄露",
	        "extra":"",
		    "info":"dubbo 接口暴漏"
	        }
	return plugin_info

def poc(hostname, port, service):
	if service == 'unknown':
		try:
			socket.setdefaulttimeout(5)
			sock = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
			address = (hostname, int(port))
			sock.connect(address)
			sock.send(b"\n")
			time.sleep(1)
			if b'dubbo' in sock.recv(10):
				# print("Success")
				return True, False
		except:
			pass
	# print("Fail")
	return False,False
