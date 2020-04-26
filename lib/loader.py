#!/usr/bin/env python
# -*- coding: utf-8 -*-
# @Time    : 19/11/8 15:31
# @Author  : Chaos
# @File    : loader.py

import os
import importlib
import json
import requests
from lib.log import log
from importlib.abc import Loader


CURRENT_DIR = os.path.abspath(os.path.dirname(os.path.dirname(__file__)))
# 获取POC的目录
POC_DIR = CURRENT_DIR + '/poc/'
# print (POC_DIR)
# POC根据目录名称划分为每一个模块
MODULES = os.listdir(POC_DIR)
# 加载POC的时候两种方式，单个POC的脚本，单个POC的模块，加载这个文件夹下的所有POC



class SinglePoc(Loader):
	def __init__(self, filename):
		self.filename = filename
		self.data = None

		if self.filename.find('.py') < 0:
			self.filename += '.py'


	def get_poc_path(self):
		for dir in MODULES:
			for root, dirs, files in os.walk(POC_DIR + dir):
				if self.filename in files:
					return root + '/' + self.filename


	def get_poc_data(self):
		log.info("POC_Path is %s", self.get_poc_path())
		with open(self.get_poc_path(), encoding='utf-8') as f:
			data = f.read()
		return data

	def exec_module(self, module):
		filepath = self.get_poc_path()
		poc_code = self.get_poc_data()
		obj = compile(poc_code, filepath, 'exec')
		exec(obj, module.__dict__)


# class ModulePoc(SinglePoc):
# 	def __init__(self, dirs):
# 		self.dirs = dirs
# 		# self.pocs = []
# 		# self.objs = []

"""
:return 获取目录下的所有poc
"""
def get_module_pocs(dir):
	pocs = []
	for root, dirs, files in os.walk(POC_DIR + dir):
		for file in files:
			if os.path.splitext(file)[-1] == ".py":
				# self.pocs.append(file)
				pocs.append(file)
	return pocs

	# def get_dir_objs(self):
	# 	self.get_module_pocs()
	# 	for _ in self.pocs:
	# 		self.objs.append(load_code_to_obj(_, self.dirs))
	# 	return self.objs

def load_code_to_obj(filename, dir='tmp'):
	poc_loader = SinglePoc(filename)
	spec = importlib.util.spec_from_file_location(dir, poc_loader.get_poc_path(), loader = poc_loader)
	mod = importlib.util.module_from_spec(spec)
	spec.loader.exec_module(mod)
	return mod


def notice(message):
	#TODO 修改钉钉通知
	robots = "https://oapi.dingtalk.com/robot/send?access_token="
	data = {"msgtype":"text","text":{"content":message},"at":{"atMobiles":[""],"isAtAll":"false"}}
	requests.post(robots,data=json.dumps(data),headers={"Content-Type":"application/json"})

