#!/usr/bin/env python
# -*- coding: utf-8 -*-
# @Time    : 20/3/17 10:58
# @Author  : Chaos
# @File    : settings.py

from flask_restful import Resource, reqparse
from flask import jsonify
from lib.mongo import db


class AddTag(Resource):
    def post(self):
        parser = reqparse.RequestParser()
        parser.add_argument('tag_name', type=str)
        parser.add_argument('tag_desc', type=str)
        args = parser.parse_args()
        tag_name = args.get('tag_name')
        tag_desc = args.get('tag_desc')
        if db.settings.find_one({"key": "tag", "tag_name": tag_name}):
            db.settings.update_one({"key": "tag", "tag_name": tag_name}, {"$set": {"tag_desc": tag_desc}}, upsert=True)
            return jsonify({"msg": "更新Tag成功"})
        else:
            db.settings.insert({"key": "tag", "tag_name": tag_name, "tag_desc": tag_desc})
            return jsonify({"msg": "ok"})

    def get(self):
        db.settings.update_many({"key": "tag"},
                                {"$set": {"hostsDistinct": [], "deviceCount": 0, "vulCount": 0, "spiderCount": 0
                                    , "hostCount": 0}})
        distinct_hosts()
        count_hosts()
        count_devices()
        count_vul()
        count_spider()
        ret = {
            "entry": list(db.settings.find({"key": "tag"}, {'_id': 0, 'hostsDistinct': 0}))
        }
        return jsonify(ret)

    def delete(self):
        parser = reqparse.RequestParser()
        parser.add_argument('tag_name', type=str)
        args = parser.parse_args()
        tag_name = args.get('tag_name')
        #
        print(tag_name)
        count = tuple(list(db.settings.find({"tag_name": tag_name}, {"_id": 0, "vulCount": 1, "deviceCount": 1,
                                                                     "spiderCount": 1}))[0].values())
        print(count)
        # if any(count):
        # 	return jsonify({"msg": "标签下存在主机，无法被删除"})

        if tag_name == 'Default':
            return jsonify({"msg": "默认标签无法被删除"})
        if db.settings.delete_one({"key": "tag", "tag_name": tag_name}).deleted_count > 0:
            return jsonify({"msg": "ok"})
        else:
            return jsonify({"msg": "删除标签失败"})


def count_hosts():
    hostCount = list(db.settings.aggregate([
        {
            "$project": {
                "hostCount": {"$size": "$hostsDistinct"},
                "tag_name": "$tag_name"
            }
        }
    ]))
    for i in hostCount:
        tag_name = i["tag_name"]
        count = i["hostCount"]
        print(tag_name, count)
        db.settings.update_one({"tag_name": tag_name}, {"$set": {"hostCount": count}}, upsert=True)


def distinct_hosts():
    host_count = list(db.portInfo.aggregate([
        {
            "$lookup": {
                "from": "settings",
                "localField": "tag_name",
                "foreignField": "tag_name",
                "as": "host_temp"
            }
        },
        # {
        # 	"$unwind": "$host_temp"
        # },
        {
            "$group": {

                "_id": {"tag_name": "$tag_name"},
                # "count": {"$sum": 1},
                "hosts": {"$addToSet": "$url"}
            }
        }
    ]))

    # print(host_count)
    if host_count:
        for i in host_count:
            tag_name = i["_id"]["tag_name"]
            hosts = i["hosts"]
            db.settings.update_one({"key": "tag", "tag_name": tag_name}, {"$set": {"hostsDistinct": hosts}},
                                   upsert=True)


def count_devices():
    host_count = list(db.portInfo.aggregate([
        # {
        # 	"$lookup": {
        # 		"from": "settings",
        # 		"localField": "tag_name",
        # 		"foreignField": "tag_name",
        # 		"as": "host_temp"
        # 	}
        # },
        # {
        # 	"$unwind": "$host_temp"
        # },
        {
            "$group": {

                "_id": {"tag_name": "$tag_name"},
                "sets": {"$addToSet": {"host": "$ip", "port": "$port"}},
                "count": {"$sum": 1}
            }
        }
    ]))

    db.settings.update_many({"key": "tag"}, {"$set": {"deviceCount": 0}})
    if host_count:
        for i in host_count:
            tag_name = i["_id"]["tag_name"]
            hosts = len(i["sets"])
            db.settings.update_one({"key": "tag", "tag_name": tag_name}, {"$set": {"deviceCount": hosts}}, upsert=True)


def count_vul():
    spider_count = list(db.vulPoc.aggregate([
        {
            "$lookup": {
                "from": "settings",
                "localField": "tag_name",
                "foreignField": "tag_name",
                "as": "host_temp"
            }
        },
        {
            "$unwind": "$host_temp"
        },
        {
            "$match": {"black_flag": 0}
        },
        {
            "$group": {

                "_id": {"tag_name": "$tag_name"},
                "sets": {"$addToSet": "$vul_url"},
                "count": {"$sum": 1}
            }
        }
    ]))

    db.settings.update_many({"key": "tag"}, {"$set": {"vulCount": 0}})
    if spider_count:
        for i in spider_count:
            tag_name = i["_id"]["tag_name"]
            hosts = len(i["sets"])
            db.settings.update_one({"key": "tag", "tag_name": tag_name}, {"$set": {"vulCount": hosts}}, upsert=True)


def count_spider():
    spider_count = list(db.bbscan.aggregate([
        {
            "$lookup": {
                "from": "settings",
                "localField": "tag_name",
                "foreignField": "tag_name",
                "as": "host_temp"
            }
        },
        {
            "$unwind": "$host_temp"
        },
        {
            "$group": {

                "_id": {"tag_name": "$tag_name"},
                "sets": {"$addToSet": "$vul_url"},
                "count": {"$sum": 1}
            }
        }
    ]))

    db.settings.update_many({"key": "tag"}, {"$set": {"spiderCount": 0}})
    if spider_count:
        for i in spider_count:
            tag_name = i["_id"]["tag_name"]
            hosts = len(i["sets"])
            db.settings.update_one({"key": "tag", "tag_name": tag_name}, {"$set": {"spiderCount": hosts}}, upsert=True)
