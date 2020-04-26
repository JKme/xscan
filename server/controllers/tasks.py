#!/usr/bin/env python
# -*- coding: utf-8 -*-
# @Time    : 20/1/7 14:30
# @Author  : Chaos
# @File    : tasks.py
import uuid
import json
from lib.mongo import db
import datetime
from flask_restful import Resource, reqparse
from flask import jsonify, Response
from lib.DBPool import redis_conn


class AddTask(Resource):
	"""
	保存到redis
	"""
	def post(self):
		parser = reqparse.RequestParser()
		parser.add_argument('task_name', type=str)
		parser.add_argument('task_target', type=str)
		parser.add_argument('BBScan', type=bool)
		parser.add_argument('port', type=str)
		parser.add_argument('task_desc', type=str)
		parser.add_argument('pocs', action='split')
		parser.add_argument('tag_name', type=str)
		args = parser.parse_args()
		task_name = args.get('task_name')
		task_target = args.get('task_target')
		BBScan_flag = args.get('BBScan')
		tag_name = args.get('tag_name')
		ports = args.get('port')
		task_desc = args.get('task_desc')
		pocs = args.get('pocs')
		task_id = str(uuid.uuid1())
		task_date = datetime.datetime.now().strftime("%Y-%m-%d %H:%M:%S")
		pocs = pocs.split('\n') if isinstance(pocs, str) else pocs
		# print(pocs)
		data = {
			"task_id": task_id,
			"task_name": task_name,
			"task_target": task_target.split('\n'),
			"BBScan_flag": BBScan_flag,
			"tag_name": tag_name,
			"ports": ports,
			"pocs": pocs,
			"task_desc": task_desc,
			"task_add_date": task_date
		}
		db.task.insert_one(data)
		for target in task_target.split('\n'):
			_ = {
				"task_name": task_name,
				"task_id": task_id,
				"target": target,
				"tag_name": tag_name
			}
			redis_conn.lpush("before_scan", json.dumps(_))

class DelTask(Resource):
	def post(self):
		parser = reqparse.RequestParser()
		parser.add_argument('task_id', type=str)
		args = parser.parse_args()
		task_id = args.task_id
		if db.task.delete_one({"task_id": task_id}).deleted_count > 0:
			db.bbscan.delete_many({"task_id": task_id})
			db.portInfo.delete_many({"task_id": task_id})
			db.vulPoc.delete_many({"task_id": task_id})
			return jsonify({"msg": "ok"})
		else:
			return jsonify({"msg": "删除失败"})


class AddVulDesc(Resource):
	def post(self):
		parser = reqparse.RequestParser()
		# parser.add_argument('task_id', type=str)
		parser.add_argument('vul_url', type=str)
		parser.add_argument('poc', type=str)
		parser.add_argument('vul_desc', type=str)
		args = parser.parse_args()
		# task_id = args.task_id
		vul_url = args.vul_url
		poc = args.poc
		vul_desc = args.vul_desc
		query = {"vul_url": vul_url, "poc":poc}
		db.vulPoc.update_one(query, {"$set": {"vul_desc": vul_desc}}, upsert=True)


class AddVulBlack(Resource):
	def post(self):
		parser = reqparse.RequestParser()
		parser.add_argument('vul_url', type=str)
		parser.add_argument('poc', type=str)
		args = parser.parse_args()
		vul_url = args.vul_url
		poc = args.poc
		query = {"vul_url":vul_url, "poc":poc}
		# print(query)
		db.vulPoc.update_many(query, {"$set": {"black_flag": 1}})
		if not db.vulBlack.find_one(query):
			db.vulBlack.insert(query)
			return jsonify({"msg": "ok"})
		else:
			return jsonify({"msg": "拉黑失败，请检查"})


class ReplayTask(Resource):
	def post(self):
		try:
			ramdom_id = str(uuid.uuid1())
			parser = reqparse.RequestParser()
			parser.add_argument('task_id', type=str)
			args = parser.parse_args()
			task_id = args.task_id
			task_name = list(db.task.find({"task_id": task_id},{"_id":0, "task_name":1}))[0]['task_name'].split('_')[0] \
			            + '_' + ramdom_id[:3]
			task_target = list(db.task.find({"task_id": task_id},{"_id":0, "task_target":1}))[0]['task_target']
			task_date = datetime.datetime.now().strftime("%Y-%m-%d %H:%M:%S")
			BBScan_flag = list(db.task.find({"task_id": task_id},{"_id":0, "BBScan_flag":1}))[0]['BBScan_flag']
			ports = list(db.task.find({"task_id": task_id},{"_id":0, "ports":1}))[0]['ports']
			pocs = list(db.task.find({"task_id": task_id}, {"_id": 0, "pocs": 1}))[0]['pocs']
			task_desc = list(db.task.find({"task_id": task_id},{"_id":0, "task_desc":1}))[0]['task_desc']
			tag_name = list(db.task.find({"task_id": task_id}, {"_id": 0, "tag_name": 1}))[0]['tag_name']
			data = {
				"task_id": ramdom_id,
				"task_name": task_name,
				"task_target": task_target,
				"tag_name": tag_name,
				"BBScan_flag": BBScan_flag,
				"ports": ports,
				"pocs": pocs,
				"task_desc": task_desc,
				"task_add_date": task_date
			}
			db.task.insert_one(data)
			for i in task_target:
				_ = {
					"task_name": task_name,
					"task_id": ramdom_id,
					"target": i,
					"tag_name": tag_name
				}
				redis_conn.lpush("before_scan", json.dumps(_))
			return jsonify({"msg": "ok"})
		except Exception as ex:
			print(str(ex))
			return jsonify({"msg": "bad"})

class QueryTaskTarget(Resource):
	def post(self):
		parser = reqparse.RequestParser()
		parser.add_argument('task_id', type=str)
		args = parser.parse_args()
		task_id = args.task_id
		print(task_id)
		targets = list(db.task.find({"task_id":task_id},{"_id":0, "task_target":1}))[0]["task_target"]
		return targets
		# return Response('</br>'.join(targets), mimetype="text/html")
		# return targets

class QueryTask(Resource):
	def post(self):
		db.task.update_many({}, {"$set": {"DevicesCount": 0, "vulnCount": 0, "hostCount": 0}})
		count_task()
		parser = reqparse.RequestParser()
		parser.add_argument('task_name', type=str)
		parser.add_argument('task_id', type=str)
		parser.add_argument("pageSize", type=str, default=10, help='')
		parser.add_argument("currentPage", type=str, default=1, help='')
		# parser.add_argument('host', type=str)
		query = {}
		args = parser.parse_args()
		if args.task_id:
			query = {"task_id": args.task_id}
		if args.task_name:
			query = dict({"task_name": {"$regex": args.task_name, "$options":"i"}}, **query)
		pageSize = int(args.pageSize)
		currentPage = int(args.currentPage)
		total = db.task.count_documents(query)
		# print(query)
		ret = {
			"total": total,
			"entry": list(
				db.task.find(query, {"_id": 0, "task_target":0}).skip(pageSize * (currentPage - 1)).limit(pageSize).sort("task_add_date", -1))
			# 已完成  调度脚本需要统计每个任务的扫描结果，并且保存到数据库里面，这样就可以返回了
			# "vulnCount": vulnCount,
			# "BBScanCount": BBScanCount,
			# "DevicesCount": DevicesCount
		}
		return ret


class QueryTaskId(Resource):
	def post(self):
		parser = reqparse.RequestParser()
		parser.add_argument("task_id", type=str, help='')
		parser.add_argument('plugin_name', type=str) # plugin有三种: vuln, bbscan, devices
		parser.add_argument("query", type=dict, help='') # 每个模块的查询条件，一次只查询一个
		parser.add_argument("pageSize", type=str, default=10, help='')
		parser.add_argument("currentPage", type=str, default=1, help='')
		args = parser.parse_args()
		pageSize = int(args.pageSize)
		currentPage = int(args.currentPage)
		# print("query is %s" % type(args.query))
		# query = json.dumps(args.query)
		task_id = args.task_id
		query = args.query
		# print("query is %s" % query)
		# print("query is %s" % type(query))
		if args.plugin_name == 'vuln':
			# task_query = {"task_id": task_id, "black_flag": 0}
			task_query = {"task_id": task_id, "black_flag": 0}
			if query['url']:
				task_query = dict({"url":{"$regex": query['url'], "$options":"i"}}, **task_query)
			if query['port']:
				task_query = dict({"port": int(query['port'])}, **task_query)
			if query['type']:
				task_query = dict({"type": query['type']}, **task_query)
			if query['tag']:
				task_query = dict({"tag": query['tag']}, **task_query)
			print("vul query is %s" % task_query)

			total = db.vulPoc.count_documents(task_query)
			types = list(db.vulPoc.find({"task_id": task_id}, {"type": 1, "_id": 0}).distinct("type"))
			ret = {
				"types": types,
				"total": total,
				"entry": list(
					db.vulPoc.find(task_query, {"_id":0,"vul_response":0}).skip(pageSize * (currentPage - 1)).limit(pageSize).sort("last_find_date", -1)
				)
			}
		elif args.plugin_name == 'bbscan':
			task_query = {"task_id": task_id}
			if query['url']:
				task_query = dict({"url": {"$regex": query['url'], "$options":"i"}}, **task_query)
			if query['type']:
				task_query = dict({"vul_Type": query['type']}, **task_query)
			if query['title']:
				task_query = dict({"title": {"$regex": query['title'], "$options":"i"}}, **task_query)
			# print("query is %s" % task_query)

			total = db.bbscan.count_documents(task_query)
			types = list(db.bbscan.find({"task_id": task_id}, {"vul_Type": 1, "_id": 0}).distinct("vul_Type"))
			ret = {
				"types": types,
				"total": total,
				"entry": list(
					db.bbscan.find(task_query, {"_id":0}).skip(pageSize * (currentPage - 1)).limit(pageSize).sort("last_find_date", -1)
				)
			}
		elif args.plugin_name == 'device':
			task_query = {"task_id": task_id}
			if query['server']:
				task_query = dict({"server": query['server']}, **task_query)
			if query['url']:
				task_query = dict({"url": {"$regex":query['url'],"$options":"i"}}, **task_query)
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
			print("device query is %s" % task_query)

			total = db.portInfo.count_documents(task_query)
			servers = list(db.portInfo.find({"task_id": task_id}, {"server": 1, "_id": 0}).distinct("server"))
			ret = {
				"servers": servers,
				"total": total,
				"entry": list(
					db.portInfo.find(task_query, {"_id":0,"banner":0}).skip(pageSize * (currentPage - 1)).limit(pageSize).sort("last_find_date", -1)
				)
			}
		else:
			ret = {"msg": "error"}
		return ret


def count_task():
	vul_count = list(db.vulPoc.aggregate([
		{
			"$lookup": {
				"from": "task",
				"localField": "task_id",
				"foreignField": "task_id",
				"as": "task_vulPoc"
			}
		},
		{
			"$unwind": "$task_vulPoc"
		},
		{
			"$match": {"black_flag": 0}
		},
		{
			"$group": {

				"_id": {"task_id": "$task_id"},
				"count": {"$sum": 1}
			}
		}
	]))
	for i in vul_count:
	# 	print(i)
		task_id = i['_id']['task_id']
		print("task id is %s :%s" % (task_id, i['count']))
		count = i['count']
		db.task.update_one({"task_id": task_id}, {"$set": {"vulnCount": count}}, upsert=True)


	#count BBScan:
	bbscan_count = db.task.aggregate([
		{
			"$lookup": {
				"from": "bbscan",
				"localField": "task_id",
				"foreignField": "task_id",
				"as": "task_bbscan"
			}
		},
		{
			"$unwind": "$task_bbscan"
		},
		{
			"$group": {

				"_id": {"task_id": "$task_id"},
				"count": {"$sum": 1}
			}
		}
	])
	for i in list(bbscan_count):

		task_id = i['_id']['task_id']
		# print("task id is %s" % task_id)
		count = i['count']
		db.task.update_one({"task_id": task_id}, {"$set": {"BBScanCount": count}}, upsert=True)

# 端口集合

	port_count = db.task.aggregate([
		{
			"$lookup": {
				"from": "portInfo",
				"localField": "task_id",
				"foreignField": "task_id",
				"as": "task_port"
			}
		},
		{
			"$unwind": "$task_port"
		},
		{
			"$group": {

				"_id": {"task_id": "$task_id"},
				"count": {"$sum": 1}
			}
		}
	])
	for i in list(port_count):

		task_id = i['_id']['task_id']
		# print("task id is %s" % task_id)
		count = i['count']
		db.task.update_one({"task_id": task_id}, {"$set": {"DevicesCount": count}}, upsert=True)

#扫描主机总数
	hostCount = list(db.task.aggregate([
	{
		"$project": {
			"hostCount": { "$size": "$task_target"},
			"task_id": "$task_id"
		}
	}
	]))
	for i in hostCount:
		task_id = i["task_id"]
		count = i["hostCount"]
		db.task.update_one({"task_id": task_id}, {"$set": {"hostCount": count}}, upsert=True)

