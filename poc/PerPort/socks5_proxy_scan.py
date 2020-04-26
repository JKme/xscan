#!/usr/bin/env python
# -*- coding: utf-8 -*-
# @Time    : 19/11/8 16:39
# @Author  : Chaos
# @File    : gitleak.py

import socket

socket.setdefaulttimeout(5)
req_timeout = 3

def plugin_info():
	plugin_info = {
			"level":"Medium",
	        "category":"socks5代理",
	        "extra":"socks5代理",
		    "info":"socks5代理"
	        }
	return plugin_info

def poc(hostname, port, service):
	if service == 'unknown':
		VER = b"\x05"
		NAUTH = b"\x01"
		AUTH = b"\x00"
		METHOD = "\x00"
		SUCCESS = "\x00"
		SOCKFAIL = "\x01"
		try:
			sock = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
			result = sock.connect_ex((hostname, int(port)))
			if result == 0:
				sock.sendall(VER + NAUTH + AUTH)
				res = sock.recv(2)
				if res == b'\x05\x00':
					# print("socks5")
					return True, False
	# if '://' not in url:
		except Exception as e:
			print(str(e))
		# pass
			return False, False
	else:
		return False, False