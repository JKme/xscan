#!/usr/bin/env python
# -*- coding: utf-8 -*-
# @Time    : 19/11/21 10:24
# @Author  : Chaos
# @File    : common.py
import re
import os
import collections
import hashlib
import urllib3
urllib3.disable_warnings(urllib3.exceptions.InsecureRequestWarning)
from urllib.parse import urlsplit
from lib.log import log
import socket
import struct
from settings import HTTP, NAMESERVERS, SOCKET_TIMEOUT
import requests
import json
import time
import tldextract
import dns.resolver
import ssl
from lib.DBPool import redis_conn


timeout = 3
socket.setdefaulttimeout(timeout)


def filterNone(values):
	"""
	Emulates filterNone([...]) functionality

	>>> filterNone([1, 2, "", None, 3])
	[1, 2, 3]
	"""

	retVal = values

	if isinstance(values, collections.Iterable):
		retVal = [_ for _ in values if _]

	return retVal


def get_hostname_port(url):
	"""
	:param url
	"""
	if '://' not in url:
		url = 'http://%s' % url
	urlSplit = urlsplit(url)
	hostnamePort = urlSplit.netloc.split(":") if not re.search(r"\[.+\]", urlSplit.netloc) else filterNone((re.search(
		r"\[.+\]", urlSplit.netloc).group(0), re.search(r"\](:(?P<port>\d+))?", urlSplit.netloc).group("port")))
	hostname = hostnamePort[0].strip()
	scheme = (urlSplit.scheme.strip().lower() or "http")
	if len(hostnamePort) == 2:
		try:
			port = int(hostnamePort[1])
		except:
			errMsg = "invalid target URL %s" % url
			log.error(errMsg, exc_info=True)
	elif scheme in ("https", "wss"):
		port = 443
	else:
		port = 80
	if port < 1 or port > 65535:
		errMsg = "invalid target URL's port (%d)" % port
		log.error(errMsg)
	return scheme, hostname, port



def check_port_open(host, port):
	"""
	检测端口连通性
	:param host:
	:param port:
	:return:
	"""
	s = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
	s.settimeout(5.0)
	try:
		if s.connect_ex((host, int(port))) == 0:
			log.info("Check port open %s:%s is Open", host, port)
			return True
	except Exception:
		log.error('[Warning] Fail to connect to %s:%s' % (host, port), exc_info=True)
	finally:
		# s.setsockopt(socket.SOL_SOCKET, socket.SO_LINGER, struct.pack('ii', 1, 0))
		s.close()
	log.info("Check port Close %s:%s is Close", host, port)
	return False

def check_http_status(scheme, host, port, task_name, task_id, tag_name):
	"""
	检测端口的连通
	状态码的有效性
	压入redis，供bbscan扫描
	:param scheme:
	:param host:
	:param port:
	:return:
	"""
	url = "%s://%s:%s" % (scheme, host, port)
	try:
		# s = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
		# s.settimeout(5.0)
		# if s.connect_ex((url, int(port))) == 0:
		log.info('Checking Http Status Valid: %s', url)
		status_code, headers, content = http_request(url)
		if status_code:
			location = headers.get('Location', '')
			if status_code not in HTTP.IGNORE_CODE:
				if status_code in [301, 302] and location.startswith("https://"):
					scheme, host, port = get_hostname_port(location)
					status_code, headers, content = http_request(location)
				m = re.search('<title>(.*?)</title>', decode_text(content))
				title = m.group(1) if m else ''
				header = get_headers(headers)
				banner = header + decode_text(content)
				rdata = {'scheme': scheme, 'port': port, 'ip': host, 'title': title, 'status_code': status_code,
						 "banner": banner, 'task_name': task_name, 'task_id': task_id, 'tag_name': tag_name}
				redis_conn.lpush("BBScan_First", json.dumps(rdata)) #压入redis，bbscan来解析扫描
				return True
	except Exception as e:
		log.error('[Warning] Get http connection failed %s:%s' % (host, port), exc_info=True)
		return False


def http_request(url):
	"""
	:param url: http://baidu.com:443
	:return:
	"""
	try:
		c = requests.get(url, headers=HTTP.HEADERS,timeout=HTTP.TIMEOUT, verify=False, allow_redirects=False)
		status_code = c.status_code
		content = c.content   # raw的格式 bytes
		headers = c.headers
		# ret = {"headers": headers, "content":content, "status_code": status_code}
		return status_code, headers, content.decode()
	except requests.exceptions.InvalidURL:   # 处理 ../manage.py 的规则出现的异常
		pass
	except urllib3.exceptions.ProtocolError:
		pass
	except requests.exceptions.ConnectionError:
		pass
	except urllib3.exceptions.ReadTimeoutError:
		pass
	except requests.exceptions.ReadTimeout:
		pass
	except:
		log.error("get http request failed to %s" % url, exc_info=True)
		return None, None, None

def reverse_host(host):
	"""
	解析域名获取IP
	:param host: hostname
	:return: list
	"""
	ret = []
	try:
		resolver = dns.resolver.Resolver()
		resolver.nameservers = NAMESERVERS
		answer = resolver.query(host, 'A')
		for i in answer:
			ret.append(i.address)
	except Exception:
		log.error("[Warning]: resolving hostname failed: %s", host)
		return
	return ret


def get_host_ip(url):
	"""
	获取给定url的IP，并且保存到数据库
	:param url:
	:return:
	"""
	scheme, hostname, port = get_hostname_port(url)
	if not re.search(r"\A\d{1,3}\.\d{1,3}\.\d{1,3}\.\d{1,3}\Z", hostname):
		ip = reverse_host(hostname)
	else:
		ip = hostname.split()
	# data = {"ip":ip}
	# mongo_push(col, condition, data, {'date': NOW})
	# log.info("resolving hostname success %s ip is %s", url, ip)
	return ip, hostname

def get_id_md5(host, port):
	h = hashlib.md5()
	h.update("{0}:{1}".format(host, port).encode())
	return h.hexdigest()


def decode_text(txt, charset='utf-8'):
	if charset:
		try:
			return txt.decode(charset)
		except Exception as e:
			pass
	for _ in ['UTF-8', 'GB2312', 'GBK', 'iso-8859-1', 'big5']:
		try:
			return txt.decode(_)
		except Exception as e:
			pass
	try:
		return txt.decode('ascii', 'ignore')
	except Exception as e:
		pass
	log.error('Fail to decode text %s', txt, exc_info=True)
	# raise Exception('Fail to decode response Text')


def get_http_desc(url):
	title, banner, status_code = None, None, None
	try:
		c = requests.get(url, timeout=HTTP.TIMEOUT, headers=HTTP.HEADERS, verify=False)
		headers = get_headers(c.headers)
		status_code = c.status_code
		banner = headers + c.content.decode('utf-8')
		text = c.content.decode('utf-8')
		title = re.search('(?<=<title>).*(?=</title>)', text)
		if not title:
			title = None
		else:
			title = title.group()
			title = re.sub(r'\n|\t', '', title)
	except Exception:
		title = None
	return title, banner, status_code


def get_headers(headers):
	"""
	https://stackoverflow.com/questions/8519599/python-dictionary-to-string-custom-format
	:param headers:
	:return:
	"""
	header = '\r\n'.join(['%s: %s' % (key, value) for (key, value) in headers.items()])
	return header + '\r\n\r\n\r\n'


def http_detect(host, port):
	"""
	检测给定host和IP运行的是http服务，还是非http服务
	:param host:
	:param port:
	:return:
	"""
	probe = b"GET / HTTP/1.0\r\n\r\n"
	service = 'unknown'
	content = ''
	
	if int(port) == 80:
		service = 'http'
		return service, ''
	if int(port) == 443:
		service = 'https'
		return service, ''
		
	socket.setdefaulttimeout(SOCKET_TIMEOUT)
	try:
		with socket.create_connection((host, port), timeout=SOCKET_TIMEOUT) as conn:
			conn.send(probe)
			time.sleep(1)
			b = conn.recv(102400).decode()
			if b[:5] == 'HTTP/':
				service = 'http'
				return service, b
			else:
				"""183.131.28.66:10443"""
				context = ssl.create_default_context()
				context.check_hostname = False
				context.verify_mode = ssl.CERT_NONE
				with socket.create_connection((host, port), timeout=SOCKET_TIMEOUT) as conn:
					with context.wrap_socket(conn, server_hostname=host) as sconn:
						sconn.send(probe)
						time.sleep(1)
						c = sconn.recv(102400).decode()
						if c[:5] == 'HTTP/':
							service = 'https'
							return service, c
	except ConnectionResetError:
		"""183.131.28.66:31443"""
		context = ssl.create_default_context()
		context.check_hostname = False
		context.verify_mode = ssl.CERT_NONE
		with socket.create_connection((host, port), timeout=SOCKET_TIMEOUT) as conn:
			with context.wrap_socket(conn, server_hostname=host) as sconn:
				sconn.send(probe)
				time.sleep(1)
				c = sconn.recv(102400).decode()
				if c[:5] == 'HTTP/':
					service = 'https'
					return service, c
	except Exception as ex:
		log.info("http detect service unknown  for %s:%s ", host, port)
	return service, content

def check_https(content):
	if 'The plain HTTP request was sent to HTTPS port' in content:
		return 'https'

def check_80(port, hostname):
	if port == 443:
		url = 'https://{}'.format(hostname)
	if port == 80:
		url = 'http://{}'.format(hostname)
	return url


def get_header(content):
	m = re.search('<title>(.*?)</title>', content)
	title = m.group(1) if m else ''
	return title
