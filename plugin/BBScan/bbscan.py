#!/usr/bin/env python
# -*- coding: utf-8 -*-
# @Time    : 19/12/18 18:12
# @Author  : Chaos
# @File    : bbscan.py

import os
import re
import glob
import json
import requests
import datetime
from urllib.parse import urlparse
from bs4 import BeautifulSoup
from lib.DBPool import redis_conn_byte, redis_conn
from lib.mongo import db
from lib.common import http_request, get_hostname_port
from lib.log import log
from settings import ROOT_DIR
from celery import Celery


# app = Celery('tasks', broker="redis://127.0.0.1:6379/4", backend='redis://127.0.0.1:6379/4')

HTTP_TIMEOUT = 30  # 请求的超时时间为30s
MAX_DEPTH = 6  # 爬取的路径深度 /1/2/3/4/5/6
USER_AGENT = 'Mozilla/5.0 AppleWebKit/537.36 (KHTML, like Gecko) Chrome/71.0.3578.98 Safari/537.36'
HEADERS = {'User-Agent': USER_AGENT, 'Connection': 'Keep-Alive', 'Range': 'bytes=0-102400'}


p_tag = re.compile('{tag="(.*?)"}')
p_status = re.compile(r'{status=(\d{3})}')
p_content_type = re.compile('{type="(.*?)"}')
p_content_type_no = re.compile('{type_no="(.*?)"}')

def init_rules():
	"""
	加载规则到redis
	:return:
	"""
	rules_path = ROOT_DIR + '/plugin/BBScan/rules/*.txt'
	num = 1
	for rule_file in glob.glob(rules_path):
		with open(rule_file, 'r') as infile:
			vul_type = os.path.basename(rule_file)[:-4]
			for url in infile.readlines():
				url = url.strip()
				if  url.startswith('/') or url.startswith('..') or url.startswith('{') or url.startswith('?'):
					# print(vul_type, url, url.split()[0])
					_ = p_tag.search(url)
					tag = _.group(1) if _ else ''

					_ = p_status.search(url)
					status = str(_.group(1)) if _ else '0'

					_ = p_content_type.search(url)
					content_type = _.group(1) if _ else ''

					_ = p_content_type_no.search(url)
					content_type_no = _.group(1) if _ else ''

					root_only = True if url.find('{root_only}') >= 0 else False

					rule = (url.split()[0], tag, status, content_type, content_type_no, vul_type)
					str_rule = ','.join(rule)
					if root_only:
						redis_conn_byte.set("bbscan_rules_root::"+vul_type+'::'+str(num), str_rule)
					else:
						redis_conn_byte.set("bbscan_rules_common::"+vul_type+'::'+str(num), str_rule)
					num += 1
					# print(rule)


def save_black_white():
	"""
	黑白名单保存到redis，减少IO，然卵
	white_list:_*
	black_list:_*
	:return:
	"""
	re_text = re.compile('{text="(.*)"}')
	re_regex_text = re.compile('{regex_text="(.*)"}')


	#file_path = './rules/white.list'
	file_path = ROOT_DIR + '/plugin/BBScan/rules/white.list'
	num = 0
	for _line in open(file_path):

		_line = _line.strip()
		if not _line or _line.startswith('#'):
			continue
		_m = re_text.search(_line)
		if _m:
			redis_conn_byte.set("white_list:_" + str(num), _m.group(1))
			# self.text_to_find.append(_m.group(1).decode('utf-8', 'ignore'))
		else:
			_m = re_regex_text.search(_line)
			if _m:
				redis_conn_byte.set("white_list:_" + str(num), _m.group(1))
		num += 1

	#file_path = './rules/black.list'
	file_path = ROOT_DIR + '/plugin/BBScan/rules/black.list'
	num = 0
	for _line in open(file_path):
		_line = _line.strip()
		if not _line or _line.startswith('#'):
			continue
		_m = re_text.search(_line)
		if _m:
			# self.text_to_exclude.append(_m.group(1).decode('utf-8', 'ignore'))
			redis_conn_byte.set("black_list:_" + str(num), _m.group(1))
		else:
			_m = re_regex_text.search(_line)
			if _m:
				# self.regex_to_exclude.append(re.compile(_m.group(1).decode('utf-8', 'ignore')))
				redis_conn_byte.set("black_list:_" + str(num), _m.group(1))
		num += 1


def get_rule_from_redis():
	"""
	从redis里面读规则
	https://huangzhw.github.io/2019/02/01/python3-redis-encoding/
	:return:
	"""
	for k in redis_conn_byte.scan_iter("bbscan_root_rules::*"):
		# print(k)
		# rule =
		print(redis_conn_byte.get(k))
		# print(rule.decode('utf-8').split(','))
		# s=redis_conn.get('﻿bbscan_root_rules::change_log::1')
		# print(pickle.loads(redis_conn.get('﻿bbscan_root_rules::change_log::1').encode('latin1')))


def get_black_white_list():
	for k in redis_conn_byte.scan_iter("white_list*"):
		print(redis_conn_byte.get(k))


def check_white_list(content):
	"""
	检查要网页的内容是否在白名单里面，在白名单返回，不在白名单继续
	:param content:
	:return:
	"""

	try:
		for k in redis_conn_byte.scan_iter("white_list*"):
			if redis_conn_byte.get(k).decode('utf-8') in content:
				return True
			continue
	except:
		log.error("check white list error", exc_info=True)


def check_black_list(content):
	"""
	检查要网页的内容是否在白名单里面，在白名单返回，不在白名单继续
	:param content: str
	:return:
	"""

	try:
		for k in redis_conn_byte.scan_iter("black_list*"):
			if redis_conn_byte.get(k).decode('utf-8') in content:
				return True
			else:
				return False
	except:
		log.error("check white list error", exc_info=True)


class Web(object):
	def __init__(self, scheme, base_url, port, title, content, status_code, header, task_name, task_id, tag_name):
		self.base_url = base_url
		self.url = "%s://%s:%s" % (scheme,base_url,port)
		self.title = title
		self.content = content
		self.status_code = status_code
		self.header = header
		self.limit = 50  # 最多抓取100个uri
		self.urls_processed = set()
		self.uris = set()
		self._404_status = -1
		self.has_status_404 = True
		self.len_404_doc = 0
		self._check_404_status()
		self.task_name =  task_name
		self.task_id = task_id
		self.tag_name = tag_name

	def init_run(self):
		"""
		增加301跳转的判断
		:return:
		"""
		try:
			status_code, headers, content = http_request(self.url)
			location = headers.get('Location', '')
			if status_code in [301, 302] and location.startwith("https://"):
				scheme, host, port = get_hostname_port(location)
				self.url = "%s://%s:%s" % (scheme, host,port)
				status_code, headers, content = http_request(self.url)
				m = re.search('<title>(.*?)</title>', content)
				title = m.group(1) if m else ''
				self.header = headers
				self.title = title
				self.content = content
			self.get_all_uri()
		except:
			log.error("running bbscan failed", exc_info=True)


	def crawl(self, path):
		"""
		从redis里面取，分离出来content，content是bytes类型
		:param path: str
		:return:
		"""
		try:
			if path == '/':
				self.content = self.content
			else:
				headers = dict(HEADERS, Range='bytes=0-204800')
				self.content = requests.get(self.url + path, headers=headers, verify=False, allow_redirects=False, timeout=HTTP_TIMEOUT).content
			# print("content is %s" % self.content)
			log.info("BBSCan: parse link from content")
			soup = BeautifulSoup(self.content, "html.parser")
			for link in soup.find_all(['a','link','script','img']):
				url = link.get('href', '').strip() or link.get('src', '').strip()
				if url.startswith('..'):
					continue
				# print ("url is %s" % url)
				if not url.startswith('/') and url.find('//') < 0:
					url = '/' + url
				url, depth = self.cal_depth(url)
				if depth <= MAX_DEPTH:
					# child = url.strip('/').split('/')
					# for i in range(len(child)):
					# 	self.get_all_uri('/'+ '/'.join(child[:i+1]))
					# uri.append(url)
					# log.info("get first url %s", url)
					#

					if url.strip('/').find('/') > 0:  #解析/1/2/3/为/1/,/1/2/,/1/2/3/
						log.info("get url %s", url)
						child = url.strip('/').split('/')
						for i in range(len(child)):
							self.get_all_uri('/'+ '/'.join(child[:i+1]))
					else:
						self.get_all_uri(url)
					# print ("url is %s:%s" % (url, depth))
					# url 放入到队列里面
			# print("URIS is %s" % list(set(url)))  # 爬取页面的路径之后，去重
		except Exception as e:
			print("Error %s" % str(e))
			log.error("BBScan: crawl %s%s failed", self.base_url, path, exc_info=True)


	def get_all_uri(self, uri='/'):
		try:
			url = str(uri)
			# print("status_404 is %s" % self.has_status_404)
			# print(self.urls_processed)
			log.info("get path for  %s%s", self.base_url, url)
			url_pattern = url
			# url_pattern = '/' + url.strip('/') + '/'
			# url_pattern = re.sub(r'\d+', '{num}', url)
			if url_pattern in self.urls_processed or len(self.urls_processed) >= self.limit:
				log.info("BBScan STOP: processed Max Url limit: %s, Get: %s", self.urls_processed, url_pattern)
				return
			else:
				log.info("add url to processed %s", url_pattern)
				self.urls_processed.add(url_pattern)
				redis_conn_byte.lpush("bbscan_uri", self.url + url)  # 把爬取的路径放入到redis里面
				log.info('save url %s', url)
				self.save_res_to_redis(url)
			self.crawl(url)

		except Exception as e:
			print ("Get_all_Uri %s" % str(e))
			pass

	def save_res_to_redis(self, url):
		try:
			if url == "/":
				for k in redis_conn_byte.scan_iter("bbscan_rules*"):
					rule_list = redis_conn_byte.get(k).decode('utf-8').split(',')
					rule_list[0] = self.url + rule_list[0]
					ret = ','.join(rule_list) + ',' + str(self._404_status) + ',' + str(self.len_404_doc)+','+ \
					      self.task_name + ',' + self.task_id + ',' + self.tag_name
					# log.info("store bbscan root request to redis %s", ret)
					redis_conn_byte.lpush('BBScan_Second', ret)
			else:
				for k in redis_conn_byte.scan_iter("bbscan_rules_common::*"):
					rule_list = redis_conn_byte.get(k).decode('utf-8').split(',')
					rule_list[0] = self.url + url.rstrip('/') + rule_list[0]
					ret = ','.join(rule_list) + ',' + str(self._404_status) + ',' + str(self.len_404_doc)+','+ \
					      self.task_name + ',' + self.task_id + ',' + self.tag_name
					# log.info("store bbscan common request to redis %s", ret)
					redis_conn_byte.lpush('BBScan_Second', ret)
		except:
			log.error("save to redis error", exc_info=True)
			pass

	def _check_404_status(self):
		try:
			try:
				c = requests.get(self.url + '/fjkgofdjgosdjfjd-404-existence-check', verify=False, timeout=HTTP_TIMEOUT, allow_redirects=False)
				self._404_status = c.status_code
				content = c.content
			except:
				log.error('[Warning] HTTP 404 check failed <%s>', self.url, exc_info=True)
				self._404_status, content = -1, ''
			if self._404_status == 404:
				self.has_status_404 = True
			else:
				self.has_status_404 = False
				self.len_404_doc = len(content)
		except:
			log.error('[Check_404] Exception %s', self.url, exc_info=True)


	def cal_depth(self, url):
		if url.find('#') >= 0:
			url = url[:url.find('#')]  # cut off fragment
		if url.find('?') >= 0:
			url = url[:url.find('?')]  # cut off query string
		if url.startswith('//'):
			return '', 10000  # //www.baidu.com/index.php
		if not urlparse(url, 'http').scheme.startswith('http'):
			return '', 10000  # no HTTP protocol
		if url.lower().startswith('http'):
			_ = urlparse(url, 'http')
			if _.netloc == self.base_url:  # same hostname
				url = _.path
			else:
				return '', 10000  # not the same hostname
		while url.find('//') >= 0:
			url = url.replace('//', '/')
		if not url:
			return '/', 1  # http://www.example.com
		if url[0] != '/':
			url = '/' + url
		url = url[: url.rfind('/') + 1]
		if url.split('/')[-2].find('.') > 0:
			url = '/'.join(url.split('/')[:-2]) + '/'
		depth = url.count('/')
		return url, depth