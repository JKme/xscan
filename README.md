
mongDB的服务端数据库要求版本>=3.6

腾讯的TSS扫描器框架:  <https://mp.weixin.qq.com/s/uT8PmlKEAZkouIe8wAkLaA>
1. 腾讯的TSS扫描器框架里面，有识别ssl的方式，可以根据实际的ssl通信过程来判断https协议
2. 发送POC的requests需要封装为一个库
3. 增加UA的随机性



## 安装:

```sh
redis-server
mkdir logs
echo > logs/error.log
echo > logs/info.log
pip3 install -r requirements.txt
use xscan
db.createUser({ user: "xscan", pwd: "xscan", roles: [{ role: "userAdminAnyDatabase", db: "admin" }] })

gunicorn -b127.0.0.1:8888 --chdir /opt/scan/server api:app
cd celerynode
celery -A tasks worker -l info
cd ../plugin
celery -A tasks worker -l info
python subscribe.py
```



### TODO:
1. 白名单不跑POC，和BBScan共享一个白名单
2. 增加同IP部署的网站
3. 增加C段存活的主机现实
4. 优化celery扫描速度

### 参考:
* <https://github.com/lijiejie/BBScan.git>
* <https://github.com/Xyntax/POC-T.git>
* <https://github.com/w-digital-scanner/w11scan>
* <https://github.com/superhuahua/xunfengES.git>
* <https://github.com/w-digital-scanner/w12scan-client.git>
* <https://github.com/al0ne/Vxscan.git>
