# coding: utf-8

import redis
import threading
import datetime
from lib.log import log
from settings import RedisConfig

NOW = datetime.datetime.now().strftime("%Y-%m-%d %H:%M:%S")
redis_lock = threading.Lock()

# decode_responses=True 如果不带这个，取出来的是Byte类型，加上之后就是str类型
def redis_conn():
	try:
		poolBR = redis.ConnectionPool(host=RedisConfig.HOST, port=RedisConfig.PORT,
		                              password=RedisConfig.PASSWORD, db=RedisConfig.BR, decode_responses=True,
		                              health_check_interval=10, socket_keepalive=True)
		# logger.info("Connect Redis Successful")
		return redis.Redis(connection_pool=poolBR)
	except Exception:
		log.error("Redis Connect Error", exc_info=True)
		return 'None'


def redis_conn_byte():
	try:
		poolBR = redis.ConnectionPool(host=RedisConfig.HOST, port=RedisConfig.PORT,
		                              password=RedisConfig.PASSWORD, db=RedisConfig.BYTE_BR,
		                              decode_responses=False,health_check_interval=10, socket_keepalive=True)
		# logger.info("Connect Redis Successful")
		return redis.Redis(connection_pool=poolBR)
	except Exception:
		log.error("Redis Connect Error", exc_info=True)
		return 'None'

def redis_strict_conn():
	try:
		r = redis.StrictRedis(host=RedisConfig.HOST, port=RedisConfig.PORT, password=RedisConfig.PASSWORD, db=RedisConfig.BR, decode_responses=True)
		return r
	except Exception:
		log.error("Redis Connect Error", exc_info=True)
		return 'None'

redis_conn = redis_conn()
redis_conn_byte = redis_conn_byte()






# def redis_sub_url(channel):
# 	_ = redis_strict()
# 	p = _.pubsub()
# 	p.subscribe(channel)
# 	return p
#
#

# def redis_pub_url(channel, url):
# 	"""
# 	redis发布函数
# 	"""
# 	p = redis_strict_conn()
# 	p.publish(channel, url)
# 	return

