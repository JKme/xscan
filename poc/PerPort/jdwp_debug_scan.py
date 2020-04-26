#!/usr/bin/env python
# -*- coding: utf-8 -*-
# @Time    : 20/3/9 13:20
# @Author  : Chaos
# @File    : jdwp_debug_scan.py.py
import socket

socket.setdefaulttimeout(5)

def plugin_info():
	plugin_info = {
			"level":"High",
	        "category":"远程命令执行",
	        "extra":"JDWP-DEBUG",
		    "info":"JDWP-DEBUG远程命令执行"
	        }
	return plugin_info

def poc(hostname, port, service):
	if service == 'unknown':
		client = socket.socket()
		try:

			client.connect((hostname, int(port)))
			client.send(b"JDWP-Handshake")
			if client.recv(14).decode() == "JDWP-Handshake":
				return True, False
		except Exception as e:
			print(str(e))
			pass
		finally:
			client.close()
	return False, False
