#!/usr/bin/env python
# -*- coding: utf-8 -*-
# @Time    : 20/3/18 11:13
# @Author  : Chaos
# @File    : group.py

from lib.mongo import db
from flask_restful import Resource, reqparse
from flask import jsonify


class QueryTagDetail(Resource):
	def post(self):
		parser = reqparse.RequestParser()
		parser.add_argument("tag_name", type=str, help='')
		parser.add_argument('plugin_name', type=str) # plugin有三种: vuln, bbscan, devices
		parser.add_argument("query", type=dict, help='') # 每个模块的查询条件，一次只查询一个
		parser.add_argument("pageSize", type=str, default=10, help='')
		parser.add_argument("currentPage", type=str, default=1, help='')
		args = parser.parse_args()
		pageSize = int(args.pageSize)
		currentPage = int(args.currentPage)
		# print("query is %s" % type(args.query))
		# query = json.dumps(args.query)
		tag_name = args.tag_name
		query = args.query
		print("query is %s" % query)
		# print("query is %s" % type(query))
		if args.plugin_name == 'vuln':
			task_query = {"tag_name": tag_name,"black_flag":0}
			if query['url']:
				task_query = dict({"url":query['url']}, **task_query)
			if query['port']:
				task_query = dict({"port": int(query['port'])}, **task_query)
			if query['type']:
				task_query = dict({"type": query['type']}, **task_query)
			if query['tag']:
				task_query = dict({"tag": query['tag']}, **task_query)

			device_detail = db.vulPoc.aggregate([
				{
					"$match": task_query
				},
				{
					"$sort": {"last_find_date": -1}
				},
				{
					"$group": {"_id": "$vul_url", "document": {"$first": "$$ROOT"}},
				},
				{
					"$skip": pageSize * (currentPage - 1)
				},
				{
					"$limit": pageSize
				}
			])
			detail = []
			types = []
			for i in list(device_detail):
				del i['document']['_id']
				detail.append(i['document'])
				types.append(i['document']['type'])
			types = list(set(types))  # 去重

			ret = {
				"servers": types,
				"total": list(db.settings.find({"key":"tag","tag_name":tag_name},{"vulCount":1,"_id":0}))[0]['vulCount'],
				"entry": detail
			}
		elif args.plugin_name == 'bbscan':
			task_query = {"tag_name": tag_name}
			if query['url']:
				task_query = dict({"url": {"$regex": query['url'], "$options":"i"}}, **task_query)
			if query['type']:
				task_query = dict({"vul_Type": query['type']}, **task_query)
			if query['title']:
				task_query = dict({"title": {"$regex": query['title'], "$options":"i"}}, **task_query)

			bbscan_detail = db.bbscan.aggregate([
					{
						"$match": task_query
					},
					{
						"$sort": {"last_find_date": -1}
					},
					{
						"$group": {"_id": "$vul_url", "document": {"$first": "$$ROOT"}},
					},
					{
						"$skip": pageSize * (currentPage - 1)
					},
					{
						"$limit": pageSize
					}
			])

			detail = []
			types = []
			for i in list(bbscan_detail):
				del i['document']['_id']
				detail.append(i['document'])
				types.append(i['document']['vul_Type'])
			types = list(set(types))   #去重

			ret = {
				"types": types,
				"total": list(db.settings.find({"key":"tag","tag_name":tag_name},{"spiderCount":1,"_id":0}))[0]['spiderCount'],
				"entry": detail
			}
			# print(ret)
			return jsonify(ret)
		elif args.plugin_name == 'device':
			task_query = {"tag_name": tag_name}
			if query['server']:
				task_query = dict({"server": query['server']}, **task_query)
			if query['ip']:
				task_query = dict({"ip": query['ip']}, **task_query)
			if query['port']:
				task_query = dict({"port": int(query['port'])}, **task_query)
			if query['status_code']:
				task_query = dict({"status_code": query['status_code']}, **task_query)
			if query['title']:
				task_query = dict({"title": {"$regex": query['title'], "$options":"i"}}, **task_query)
			if query['banner']:
				task_query = dict({"banner": {"$regex": query['banner'], "$options":"i"}}, **task_query)

			device_detail = db.portInfo.aggregate([
					{
						"$match": task_query
					},
					{
						"$sort": {"last_find_date": -1}
					},
					{
						"$group": {"_id": {"ip":"$ip","port":"$port"},"document": {"$first": "$$ROOT"}},
					},
					{
						"$skip": pageSize * (currentPage - 1)
					},
					{
						"$limit": pageSize
					}
			])
			detail = []
			servers = []
			for i in list(device_detail):
				del i['document']['_id']
				detail.append(i['document'])
				servers.append(i['document']['server'])
			servers = list(set(servers))   #去重

			ret = {
				"servers": servers,
				"total": list(db.settings.find({"key":"tag","tag_name":tag_name},{"deviceCount":1,"_id":0}))[0]['deviceCount'],
				"entry": detail
			}
		else:
			ret = {"msg": "error"}
		return ret


class QueryTagTarget(Resource):
	def post(self):
		parser = reqparse.RequestParser()
		parser.add_argument('tag_name', type=str)
		args = parser.parse_args()
		tag_name = args.tag_name
		print(tag_name)
		targets = list(db.settings.find({"key":"tag","tag_name":tag_name},{"_id":0, "hostsDistinct":1}))[0]["hostsDistinct"]
		return targets