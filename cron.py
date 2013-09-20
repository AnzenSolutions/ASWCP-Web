#!/usr/bin/env python

from apscheduler.scheduler import Scheduler
from apscheduler.jobstores.shelve_store import ShelveJobStore
from konf import Konf
from time import time

import redis
import db
import threading

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

"""
Make cron check Redis db for queued up tasks then push them out to the machine, receive input then store in db.  
Do this in threads so there is no locking of long tasks.
"""
def cron():
    print "testing cron"

sched = Scheduler(daemonic=False)
sched.add_jobstore(ShelveJobStore('./cron.jobs'), 'file')
sched.add_interval_job(cron, seconds=10)
sched.start()
