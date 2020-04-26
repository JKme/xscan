#!/usr/bin/env python
# -*- coding: utf-8 -*-
# @Time    : 20/1/7 13:35
# @Author  : Chaos
# @File    : portal.py
from lib.mongo import db
from flask import jsonify, json
from flask_restful import Resource, reqparse

class Count(Resource):
	def get(self):
		vul_count = db.vulPoc.count_documents({})
		host_count = len(db.portInfo.distinct("ip"))
		port_count = db.portInfo.count_documents({})
		bbscan_count = db.bbscan.count_documents({})
		data = {"vul": vul_count, "host": host_count, "port": port_count, "bbscan": bbscan_count}
		return jsonify(data)


class Detail(Resource):
	def get(self):
		result = list(db.vulPoc.find({}, {'_id': 0}))
		return result


class Query(Resource):
	def post(self):
		parser = reqparse.RequestParser()
		parser.add_argument("url", type=str, help='')
		parser.add_argument("port", type=str, help='')
		parser.add_argument("type", type=str, help='')
		parser.add_argument("tag", type=str, help='')
		parser.add_argument("pageSize", type=str, default=10, help='')
		parser.add_argument("currentPage", type=str, default=1, help='')
		args = parser.parse_args()
		query = {}
		if args.url:
			query = {"url": args.url}
		if args.port:
			query = dict({"port": int(args.port)}, **query)
		if args.type:
			query = dict({"type": args.type}, **query)
		if args.tag:
			query = dict({"tag": args.tag}, **query)
		pageSize = int(args.pageSize)
		currentPage = int(args.currentPage)
		total = db.vulPoc.count_documents(query)
		ret = {
			"total": total,
			"entry": list(db.vulPoc.find(query, {"_id":0}).skip(pageSize * (currentPage-1)).limit(pageSize).sort('last_find_date', -1))
		}
		return ret
		# return jsonify({"data":list(db.vulPoc.find(filter, {"_id":0}))})
		# print (json.request.data.decode('utf-8'))


	def get(self):
		return list(db.vulPoc.find({}, {"type": 1, "_id": 0}).distinct("type"))

class GetVulTypes(Resource):
	def get(self):
		return list(db.vulPoc.find({}, {"type": 1, "_id":0}).distinct("type"))


class QueryVul(Resource):
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
		if query['url']:
			task_query = dict({"url": {"$regex":query['url']}}, **task_query)
		if query['port']:
			task_query = dict({"port": int(query['port'])}, **task_query)
		if query['poc']:
			task_query = dict({"poc": {"$regex":query['poc']}}, **task_query)
		# if query['vul_url']:
		# 	task_query = dict({"vul_url": {"$regex": query['vul_url']}}, **task_query)
		if query['level']:
			task_query = dict({"level":  query['level']}, **task_query)
		if query['type']:
			task_query = dict({"type":  query['type']}, **task_query)
		print("Vul Query is %s" % task_query)
		# servers = list(db.portInfo.find(task_query, {"server": 1, "_id": 0}).distinct("server"))
		types = list(
			db.vulPoc.aggregate([
				{
					"$match": task_query
				},
				{
					"$group": {
						"_id": {"types": "$type"}
					}
				}
			])
		)
		ret_types = []
		for s in types:
			ret_types.append(s["_id"]["types"])


		vuls = list(
			db.vulPoc.aggregate([{"$match":
				task_query
		 },
		{
			"$sort": {
				"last_find_date":-1
			}
		},
		# {"$unwind": "$data"},
		{"$group":
			 {"_id": {"url": "$url", "port": "$port", "poc": "$poc"},
			  "last_find": {"$max":"$last_find_date"},
			  "first_find": {"$min": "$first_find_date"},
			  "name": {"$first": "$name"},
			  "level": {"$first": "$level"},
			  "type": {"$first": "$type"},
			  "vul_url": {"$first": "$vul_url"},
			  "black_flag": {"$first": "$black_flag"},
			  "vul_response": {"$first": "$vul_response"},
			  # "serversxxs":{"$addToSet":"$server"}
			# "data": { "$addToSet": "$$ROOT" }
			  }
		},
		{
		"$sort":{"last_find":-1}  # 返回值按照最新发现时间正排列
		}
		]))
		total = len(vuls)
		# print("device is %s" % vuls)
		vuls_id = vuls[(currentPage -1 )*pageSize : pageSize*currentPage ]
		# print("device_id is %s" % vuls_id)
		res = []
		for i in vuls_id:
			url = i["_id"]["url"]
			port = i["_id"]["port"]
			poc = i["_id"]["poc"]
			name = i["name"]
			level = i["level"]
			types = i["type"]
			vul_url = i["vul_url"]
			vul_response = i["vul_response"]
			first_find_date = i["first_find"]
			last_find_date = i["last_find"]
			black_flag = i["black_flag"]
			data = {"url":url, "port":port,"poc":poc,"name":name,"level":level,"first_find_date":first_find_date,
			        "last_find_date":last_find_date, "type": types, "vul_url":vul_url, "vul_response":vul_response, "black_flag":black_flag }
			res.append(data)
			# print(res)
			# print("res is %s" % res)
		ret = {
			"total": total,
			"types": ret_types,
			"entry": res,
		}
		return ret