import tornado.web
from time import time
import hashlib
import hmac
import traceback
from plugins.bases.plugin import PluginBase
import os
import sys
import sha3
import socket
import json
from base64 import b64encode as encode,b64decode as decode
from random import getrandbits,choice

class HandlersBase(tornado.web.RequestHandler, PluginBase):
	# Every handler must have a web path, override this in this fashion
	WEB_PATH = r"/"
	STORE_ATTRS = True
	STORE_UNREF = True

	# Specifies what JS and CSS files to load from templates/bootstrap/[css|js]
	JS_FILES = []
	CSS_FILES = []

	# Used as a default for every page
	PAGE_TITLE = "Home"

	# Optional options to pass when the class is initialized in Tornado
	OPTS = {}
	def create_id(self, req, pub, priv):
		return encode(hashlib.sha256(str(getrandbits(2048))).digest(),choice(['rA', 'aZ','gQ','hH','hG','aR','DD'])).rstrip("==")

	def make_request(self, id, req, pub, priv):
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
		self.redis.set("%s" % id, msg_sig.hexdigest())

		return "%s:%s:%s:%s" % (id, pub, msg_sig.hexdigest(), body)

	def get_response(self, sock):
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
				self.redis.delete(rid)
				return d['data']

		return False

	def client(self, ip, msg="", ipv6=False, port=5222, pub="", priv=""):
		reqid = self.create_id(msg,pub,priv)

		# Only do IPv6 checks if server supports IPv6
		if ipv6 and socket.has_ipv6:
			sock = socket.socket(socket.AF_INET6, socket.SOCK_STREAM)
		else:
			sock = socket.socket(socket.AF_INET, socket.SOCK_STREAM)

		try:
			sock.connect((ip, port))
		except:
			return False

		#print "> Sending request to",ip

		sock.sendall(self.make_request(reqid, msg, pub, priv) + "\n")

		return self.get_response(sock)

	def initialize(self, **kwargs):
		self.db = kwargs.get("db", None)
		self.redis = kwargs.get("redis", None)
		self.sysconf = kwargs.get("sysconf", None)
		
		self.uid = self.get_secure_cookie('id')

	@property
	def get_uid(self):
		return self.uid

	def logged_in(self):
		return True if self.uid != None else False

	def get_uname(self,conv_none=True):
		if conv_none and self.user == None:
			return ""
		else:
			return self.user

	def text2hash(self, text2hash):
		enc = hashlib.sha3_512()
		enc.update(str(text2hash).encode("utf-8"))
		return enc.hexdigest()

	def get_template_path(self):
		return "%s/templates" % os.path.dirname(os.path.realpath(sys.argv[0]))

	@property
	def get_un(self):
		return self.get_secure_cookie("un")

	def get_keys(self, srvid):
		keys = json.loads(self.redis.get("%s_keys" % self.get_secure_cookie("un")))

		try:
			return keys["%d" % srvid]
		except KeyError:
			return None
			
	"""
	show

	Wrapper around RequestHandler's render function to make rendering these templates easier/better.
	This way the class just has to specify what special CSS and/or JavaScript files to load (see handlers/main),
	and it is automatically passed to the template engine to parse and deal with.

	Easier management and use IMO.
	"""
	def show(self, templ, **kwargs):
		alert_title = "Notice!"
		
		if "alert_title" in kwargs:
			alert_title = kwargs["alert_title"]
			del kwargs["alert_title"]

		js = ["jquery", "bootstrap.min", "common"]
		js.extend(self.JS_FILES)

		css = ["common"]
		css.extend(self.CSS_FILES)
		
		show_menu = self.logged_in()

		if "show_menu" in kwargs:
			show_menu = kwargs["show_menu"]
			del kwargs["show_menu"]

		self.render("%s.html" % templ, js=js, css=css, page_title=self.PAGE_TITLE, alert_title=alert_title, show_menu=show_menu, user=self.get_un, **kwargs)

	def write_error(self, status_code, **kwargs):
		path = os.path.dirname(os.path.realpath(sys.argv[0]))

		ref,err,tb = kwargs['exc_info']

		trace = "\n"

		for t in traceback.format_tb(tb):
			trace += t

		eid = encode(hashlib.md5(trace + str(time())).digest())

		msg = "Unfortunately an error has occured.  If you believe this is in error, please contact support.<br /><br />"
		msg += "In contacting support, please also reference the unique ID for this issue: %s" % (eid)
		msg += "<br /><br />Error: %s" % (err)

		#db.insert(tbl="syserr").data({"id" : eid, "ts" : now(), "err" : err, "tb" : trace, "user_id" : self.get_uid()}).run

		self.show("%s/templates/message.html" % path, path=path, page_title="Error", ADMIN=self.get_uid, message=msg)
