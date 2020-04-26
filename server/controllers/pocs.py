#!/usr/bin/env python
# -*- coding: utf-8 -*-
# @Time    : 20/2/14 14:02
# @Author  : Chaos
# @File    : pocs.py
from flask_restful import Resource, reqparse
from flask import jsonify
from lib.mongo import db

class QueryPoc(Resource):
	def post(self):
		parser = reqparse.RequestParser()
		parser.add_argument("folders", default='', type=str, help='')
		parser.add_argument("poc", default='', type=str, help='')
		parser.add_argument("level", default='', type=str, help='')
		parser.add_argument("category", default='', type=str, help='')
		parser.add_argument("pageSize", type=str, default=10, help='')
		parser.add_argument("currentPage", type=str, default=1, help='')
		args = parser.parse_args()
		query = {}
		if args.folders:
			query = {"folder": args.folders}
		if args.poc:
			query = dict({"poc": {"$regex": args.poc, "$options":"i"}}, **query)
		if args.level:
			query = dict({"level": args.level}, **query)
		if args.category:
			query = dict({"category": args.category}, **query)
		pageSize = int(args.pageSize)
		currentPage = int(args.currentPage)
		# print(query)
		total = db.plugin.count_documents(query)
		ret = {
			"total": total,
			"entry": list(db.plugin.find(query, {"_id":0}).skip(pageSize * (currentPage-1)).limit(pageSize).sort("mtime", -1))
		}
		return ret

	def get(self):
		folders = list(db.plugin.find({}, {"folder": 1, "_id": 0}).distinct("folder"))
		category = list(db.plugin.find({}, {"category": 1, "_id": 0}).distinct("category"))
		ret = {
			"folders": folders,
			"category": category
		}
		return ret