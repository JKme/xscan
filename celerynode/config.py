#!/usr/bin/env python
# -*- coding: utf-8 -*-
# @Time    : 19/11/6 16:38
# @Author  : Chaos
# @File    : config.py


class CeleryConfig():
	BROKER_URL = "redis://127.0.0.1:6379"
	# BACKEND_URL = "redis://127.0.0.1:6379"
	CELERY_TASK_SERIALIZER = "json"
	CELERY_TIMEZONE = "Asia/Shanghai"
	# CELERY_ROUTES = {
	# 	'celerynode.tasks.poc_scan':{'exchange': 'topic', 'routing_key':'domain.key'}
	# }