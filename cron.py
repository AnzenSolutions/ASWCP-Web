#!/usr/bin/env python

import logging
import sys

root = logging.getLogger()
ch = logging.StreamHandler(sys.stdout)
ch.setLevel(logging.DEBUG)
formatter = logging.Formatter('%(asctime)s - %(name)s - %(levelname)s - %(message)s')
ch.setFormatter(formatter)
root.addHandler(ch)

from apscheduler.scheduler import Scheduler
from apscheduler.jobstores.shelve_store import ShelveJobStore
from konf import Konf
from time import time
from base64 import b64encode as encode,b64decode as decode
from random import getrandbits,choice

import redis
import db
import threading
import sha3
import socket
import json
import hashlib

_BASE_DEFAULTS = {
	'command_parse' : "",
	'arg_sep' : " ",
	'port' : 1337,
	'debug' : True,
	'cookie_secret' : 'monster',
	'redis_host' : 'localhost',
	'redis_port' : 6379,
	'redis_db' : 0,
	'sql_driver' : "postgre",
	'sql_host' : "localhost",
	'sql_user' : "postgres",
	"sql_pass" : "c",
	'sql_db' : "aswcp",
	"goport" : 8080,
	"gohost" : "cp.anzensolutions.com",
	"ssl_cert" : "ssl.crt",
	"ssl_key" : "ssl.key",
	
	# See _LOG_LEVELS to set
	"log_level" : "debug"
}

conf = Konf(defaults=_BASE_DEFAULTS)

# We only support PostgreSQL and SQLite so far
if conf.sql_driver == "postgre":
	db.database.init(conf.sql_db, user=conf.sql_user, password=conf.sql_pass, host=conf.sql_host)
elif conf.sql_driver == "sqlite":
	db.database.init(conf.sql_db)
else:
	raise Exception("Improper database type.  Please set sql_driver to one of the following: postgre, sqlite")
		
# Safety precaution
db.database.connect()

# Set up a Redis connection
pydis = redis.StrictRedis(host=conf.redis_host, port=conf.redis_port, db=conf.redis_db)

def create_id(req, pub, priv):
	return encode(hashlib.sha256(str(getrandbits(2048))).digest(),choice(['rA', 'aZ','gQ','hH','hG','aR','DD'])).rstrip("==")

def make_request(id, req, pub, priv):
	tmp = req.split(" ")
	cmd = tmp[0]
	args = []

	enc = hashlib.sha3_512()
	enc.update(priv.encode('utf-8'))

	try:
		args = tmp[1:]
	except:
		pass

	body = encode("%s" % (json.dumps({"cmd" : cmd, "args" : args})))
	
	msg_sig = hmac.new(str(priv), body, hashlib.sha512)
	pydis.set("%s" % id, msg_sig.hexdigest())

	return "%s:%s:%s:%s" % (id, pub, msg_sig.hexdigest(), body)

def get_response(sock):
	dat = ""
	tmp = ""

	while True:
		tmp = str(sock.recv(1024))

		if tmp != "":
			dat = "%s%s" % (dat, tmp)
		else:
			break
		
	if dat != "":
		try:
			rid,api,sig,resp = dat.split(":")
			d = json.loads(decode(resp))
		except ValueError:
			print "> dat:",dat
			d = json.loads(dat)
			
		if d['status']:
			pydis.delete(rid)
			return d['data']

	return False

def client(ip, msg="", ipv6=False, port=5222, pub="", priv=""):
	reqid = create_id(msg,pub,priv)

	# Only do IPv6 checks if server supports IPv6
	if ipv6 and socket.has_ipv6:
		sock = socket.socket(socket.AF_INET6, socket.SOCK_STREAM)
	else:
		sock = socket.socket(socket.AF_INET, socket.SOCK_STREAM)

	try:
		sock.connect((ip, port))
	except:
		return False
        
	sock.sendall(self.make_request(reqid, msg, pub, priv) + "\n")

	return get_response(sock)
        
class Jobs(object):
    thread_count = 4
    lock = threading.Lock()
    
    def get_jobs(self):
        return db.jobqueue.select()
    
    def remove_job(self, jid):
        return db.jobqueue.get(db.jobqueue.id==jid).delete_instance()
    
    def run(self, job):
        server_info = db.servers.select().where(db.servers.id==job.server).get()
        api_keys = db.api.select().where(db.api.server==job.server).get()
        
        data = client(server_info.ipv4, msg=job.cmd, pub=api_keys.public, priv=api_keys.private)
            
        status = 1
            
        if data == False:
            status = 0
            
        # try:    
        db.reports.create(server=job.server,ts=int(time()),msg=data,title=job.cmd,status=status)
        self.remove_job(job.id)
        # except:
        #    db.database.rollback()
    
    def start(self):
        threads = []
        
        jobs = 0
        
        last_check = 0
        
        try:
            last_check = int(pydis.get("cron_last_run"))
        except TypeError:
            pass
            
        pydis.set("cron_last_run", int(time()))
        
        for job in db.jobqueue.select().where(db.jobqueue.ts >= last_check):
            jobs += 1
            t = threading.Thread(target=self.run, args=(job,))
            t.start()
            threads.append(t)
        
        [ t.join() for t in threads ]
        
        # Started %d jobs" % jobs
            
cjob = Jobs()

sched = Scheduler(daemonic=False)
sched.add_jobstore(ShelveJobStore('./cron.jobs'), 'file')
sched.add_interval_job(cjob.start, seconds=10)
sched.start()
