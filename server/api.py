#!/usr/bin/env python
# -*- coding: utf-8 -*-
# @Time    : 20/1/7 13:32
# @Author  : Chaos
# @File    : api.py
from flask import Flask
from flask_restful import Api
from server.controllers.dashboard import Count, Detail,Query, GetVulTypes, QueryVul
from server.controllers.tasks import AddTask, QueryTask, QueryTaskId, ReplayTask,DelTask,AddVulDesc,AddVulBlack,QueryTaskTarget
from server.controllers.pocs import QueryPoc
from server.controllers.devices import QueryDevice
from server.controllers.tags import AddTag
from server.controllers.group import QueryTagDetail,QueryTagTarget
from flask_cors import CORS

app = Flask(__name__)
api = Api(app)
CORS(app, resources=r'/*')


api.add_resource(Count, '/api/dashboard/count')
api.add_resource(Detail, '/api/dashboard/detail')
api.add_resource(Query, '/api/dashboard/query')
api.add_resource(GetVulTypes, '/api/dashboard/getvultypes')
api.add_resource(QueryPoc, '/api/poc/query')
api.add_resource(AddTask, '/api/add/task')
api.add_resource(QueryTask, '/api/query/task')
api.add_resource(QueryTaskTarget, '/api/query/QueryTaskTarget')
api.add_resource(AddVulDesc, '/api/add/addVulDesc')
api.add_resource(AddVulBlack, '/api/add/addVulBlack')
api.add_resource(DelTask, '/api/del/task')
api.add_resource(QueryTaskId, '/api/query/taskDetail')
api.add_resource(QueryDevice, '/api/query/devices')
api.add_resource(QueryVul, '/api/query/vul')
api.add_resource(ReplayTask, '/api/replay/task')
api.add_resource(AddTag, '/api/settings/tag')
api.add_resource(QueryTagTarget, '/api/query/QueryTagTarget')
api.add_resource(QueryTagDetail, '/api/query/tagDetail')


if __name__ == '__main__':
	app.run(host='0.0.0.0', threaded=True, use_reloader=True)
