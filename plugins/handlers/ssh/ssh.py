from plugins.bases.handlers import HandlersBase
import json
import hashlib
import sha3
from time import time
import socket
from base64 import b64encode as encode,b64decode as decode

class ssh(HandlersBase):
    WEB_PATH = r"/ssh/([0-9]+)/?"
    STORE_ATTRS = True
    STORE_UNREF = True
    OPTS = {}

    CSS_FILES = ["gateone"]
    JS_FILES = ["gateone", "ssh"]

    def get(self, srvid):
        self.show("ssh", srvid=srvid, show_menu=False)

    def post(self, srvid):
        un = self.get_secure_cookie("un")

        keydb = json.loads(self.redis.get("%s_keys" % un))
        keys = keydb[srvid]

        server = self.db.servers.select().where(self.db.servers.id==srvid).get()
        
        sshport = self.client(server.ipv4, msg="sshport", pub=keys['public'], priv=keys['private'])
        
        # self.write("%s|%s|%s|%s" % (server.hostname,sshport,self.sysconf.gohost,self.sysconf.goport))
        self.write("%s|%s|%s|%s" % (server.ipv4,sshport,self.sysconf.gohost,self.sysconf.goport))