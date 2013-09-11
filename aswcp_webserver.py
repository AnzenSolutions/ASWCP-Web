#!/usr/bin/env python

import tornado.ioloop
import tornado.web
import tornado.httpserver

from plugins.bases.registry import find_plugins, get_plugins_of_type

from konf import Konf

import redis
import db

# We don't need to keep a reference for our sake
find_plugins()

# Store all the handlers we are going to be using
handlers = [
	(r"/css/(.*)", tornado.web.StaticFileHandler, {"path" : "./templates/bootstrap/css"}),
	(r"/js/(.*)",  tornado.web.StaticFileHandler, {"path" : "./templates/bootstrap/js"} ),
	(r"/img/(.*)", tornado.web.StaticFileHandler, {"path" : "./templates/bootstrap/img"})
]

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

settings = dict(
	debug=conf.debug,
	cookie_secret=conf.cookie_secret
)

# Set up a Redis connection
pydis = redis.StrictRedis(host=conf.redis_host, port=conf.redis_port, db=conf.redis_db)

# Get all the handler plugins
hp = get_plugins_of_type("handlers")

# Options for each handler
opts = {}

# Loop through each handler and get their set options
for name,data in hp.iteritems():
	opts = data['attrs']['OPTS'] if "OPTS" in data['attrs'] else {}
	
	# Specify a reference to the database, redis and the main config for each handler
	opts.update({'db' : db, 'redis' : pydis, 'sysconf' : conf})
	
	# What directory do they process requests for when browsed via web?
	handlers.append((data['attrs']['WEB_PATH'], data['ref'], opts))

	try:
		# If a handler requests a setting that doesn't exist, set it so we can pass it to tornado
		for k,v in data['attrs']['SETTINGS'].iteritems():
			if k not in settings:
				settings[k] = v
	except KeyError:
		pass
		
app = tornado.web.Application(handlers, **settings)

if __name__ == "__main__":
	# Originally HTTPS was forced, but now its optional (though recommended)
	if conf.ssl_cert != "" and conf.ssl_key != "":
		http_server = tornado.httpserver.HTTPServer(app, ssl_options={"certfile" : conf.ssl_cert, "keyfile" : conf.ssl_key})
	else:
		http_server = tornado.httpserver.HTTPServer(app)
		
	http_server.listen(int(conf.port))
	tornado.ioloop.IOLoop.instance().start()
