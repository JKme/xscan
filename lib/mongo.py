#!/usr/bin/env python
# -*- coding: utf-8 -*-
# @Time    : 19/11/22 13:47
# @Author  : Chaos
# @File    : mongo.py
import pymongo
import sys
from settings import NOW, MONGO
from lib.log import log

def mongo_conn():
	try:
		db = pymongo.MongoClient("mongodb://{}:{}@{}:{}/{}?authMechanism=SCRAM-SHA-1&connect=false".format(
                    MONGO.USER,
					MONGO.PASS,
                    MONGO.IP,
                    MONGO.PORT,
                    MONGO.DB))
		return db
	except Exception:
		log.error("Connect Mongodb Failed")
		sys.exit(0)

db = mongo_conn().xscan