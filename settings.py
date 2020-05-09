# coding: utf8

import os
import datetime

class RedisConfig(object):
	HOST = "localhost"
	PORT = 6379
	PASSWORD = ""
	BR = 1
	HOSTSCANKEY = "urlScan"
	VULTASKKEY = "vulTask"
	BYTE_BR = 2

class MASSCAN(object):
	PATH = '/usr/local/bin/masscan'
	RATE = '1500'

class MONGO(object):
	IP = "127.0.0.1"
	PORT = 27017
	USER = "xscan"
	PASS = "xscan"
	DB = "xscan"

NOW = datetime.datetime.now().strftime("%Y-%m-%d %H:%M:%S")

class HTTP(object):
	IGNORE_CODE = [500, 502, 504]
	HEADERS = {
	'Accept': 'text/html,application/xhtml+xml,application/xml;q=0.9,*/*;q=0.8',
	# 'Content-Type': 'application/x-www-form-urlencoded',
	'User-Agent': 'Mozilla/5.0 (Windows NT 5.1; rv:5.0) Gecko/20100101 Firefox/5.0',
	'Referer': 'https://www.baidu.com',
	# 'X-Forwarded-For': ip,
	# 'X-Real-IP': ip,
	'Connection': 'keep-alive',
	}
	TIMEOUT = 30

SOCKET_TIMEOUT = 30
ROOT_DIR = os.path.abspath(os.path.dirname(__file__))
NAMESERVERS = [
    '119.29.29.29', '182.254.116.116',  # DNSPod
    '180.76.76.76',  # Baidu DNS
    '223.5.5.5', '223.6.6.6',  # AliDNS
    '114.114.114.114', '114.114.115.115'  # 114DNS
    # '8.8.8.8', '8.8.4.4',  # Google DNS
    # '1.0.0.1', '1.1.1.1'  # CloudFlare DNS
    # '208.67.222.222', '208.67.220.220'  # OpenDNS
]  # 指定查询的DNS域名服务器
