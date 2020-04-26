#!/usr/bin/env python
# -*- coding: utf-8 -*-
# @Time    : 20/3/16 16:35
# @Author  : Chaos

import socket

req_timeout = 3
def plugin_info():
	plugin_info = {
			"level":"Low",
	        "category":"信息泄露",
	        "extra":"",
		    "info": "信息泄露"
	        }
	return plugin_info


def poc(hostname, port, service):
	if service == 'unknown':
		client = socket.socket()
		try:

			client.connect((hostname, int(port)))
			client.send(b"stats\r\n")
			if "STAT version" in client.recv(1024).decode():
				return True, False
		except Exception as e:
			print(str(e))
			pass
		finally:
			client.close()
	return False, False
