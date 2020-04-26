#!/usr/bin/env python
# -*- coding: utf-8 -*-
# @Time    : 20/3/3 16:24
# @Author  : Chaos
# @File    : devices.py
from flask_restful import Resource, reqparse
from flask import jsonify
from lib.mongo import db

class QueryDevice(Resource):
	def post(self):
		parser = reqparse.RequestParser()
		parser.add_argument("query", default='', type=dict, help='')
		parser.add_argument("pageSize", type=str, default=10, help='')
		parser.add_argument("currentPage", type=str, default=1, help='')
		args = parser.parse_args()
		pageSize = int(args.pageSize)
		currentPage = int(args.currentPage)
		query = args.query
		# print("Device Query is %s" % type(query))
		# print ("server is %s" % query['server'])
		task_query = {}
		if query['server']:
			task_query = dict({"server": query['server']}, **task_query)
		if query['ip']:
			task_query = dict({"ip": query['ip']}, **task_query)
		if query['port']:
			task_query = dict({"port": int(query['port'])}, **task_query)
		if query['status_code']:
			task_query = dict({"status_code": int(query['status_code'])}, **task_query)
		if query['title']:
			task_query = dict({"title": {"$regex": query['title'], "$options":"i"}}, **task_query)
		if query['banner']:
			task_query = dict({"banner": {"$regex": query['banner'], "$options":"i"}}, **task_query)
		print("Device Query is %s" % task_query)
		# servers = list(db.portInfo.find(task_query, {"server": 1, "_id": 0}).distinct("server"))
		servers = list(
			db.portInfo.aggregate([
				{
					"$match": task_query
				},
				{
					"$group": {
						"_id": {"servers": "$server"}
					}
				}
			])
		)
		ret_servers = []
		for s in servers:
			ret_servers.append(s["_id"]["servers"])

		status = list(
			db.portInfo.aggregate([
				{
					"$match": task_query
				},
				{
					"$group": {
						"_id": {"servers": "$status_code"}
					}
				}
			])
		)
		ret_status = []
		for s in status:
			ret_status.append(s["_id"]["servers"])

		device = list(
			db.portInfo.aggregate([{"$match":
				task_query
		 },
		{
			"$sort": {
				"last_find_date":-1
			}
		},
		# {"$unwind": "$data"},
		{"$group":
			 {"_id": {"ip": "$ip", "port": "$port", "server": "$server", "title":"$title"},
			  "last_find": {"$max":"$last_find_date"},
			  "first_find": {"$min": "$first_find_date"},
			  "banner": {"$first": "$banner"},
			  "url": {"$first": "$url"},
			  "status_code": {"$first": "$status_code"},
			  # "serversxxs":{"$addToSet":"$server"}
			# "data": { "$addToSet": "$$ROOT" }
			  }
		},
		{
		"$sort":{"last_find":-1}  # 返回值按照最新发现时间正排列
		}
		]))
		total = len(device)
		# print("device is %s" % device)
		device_id = device[(currentPage -1 )*pageSize : pageSize*currentPage ]
		# print("device_id is %s" % device_id)
		res = []
		for i in device_id:
			ip = i["_id"]["ip"]
			port = i["_id"]["port"]
			server = i["_id"]["server"]
			title = i["_id"]["title"]
			banner = i["banner"]
			url = i["url"]
			# print(i["banner"])
			first_find_date = i["first_find"]
			last_find_date = i["last_find"]
			status_code = i["status_code"]
			data = {"ip":ip, "port":port,"server":server,"title":title,"banner":banner,"first_find_date":first_find_date,
			        "last_find_date":last_find_date, "status_code": status_code, "url": url}
			res.append(data)
			# print(res)
			# print("res is %s" % res)
		ret = {
			"servers": ret_servers,
			"total": total,
			"status": ret_status,
			"entry": res,
		}
		return ret