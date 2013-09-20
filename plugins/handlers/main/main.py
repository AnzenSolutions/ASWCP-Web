from plugins.bases.handlers import HandlersBase
import os
import sys
import json
from time import time

class MainHandler(HandlersBase):
    WEB_PATH = r"/"
    STORE_ATTRS = True
    STORE_UNREF = True
    OPTS = {}
    JS_FILES = ['main']

    def get(self):
        if not self.logged_in():
            self.redirect("/login")
        else:
            s = self.db.servers
            a = self.db.api
            server_list = {}
            
            servers = s.select(
                s.id.alias("sid"),s.ipv6.alias("ipv6"),s.hostname.alias("hostname"),s.ipv4.alias("ipv4"),s.added.alias("added"),
                a.id.alias("aid"),a.private.alias("private"),a.public.alias("public")
            ).join(a, self.db.JOIN_FULL).where(s.user==self.uid)
            
            status = 2

            ip = ""
            ipv6 = False
            
            for server in servers:
                status = 2

                if server.ipv4 != "":
                    ip = server.ipv4
                    ipv6 = False
                else:
                    ip = server.ipv6
                    ipv6 = True
                
                
                if server.api.public != None:
                    status = self.client(ip, ipv6=ipv6, msg="heartbeat", pub=server.api.public, priv=server.api.private)
                    
                server_list[server.hostname] = {
                    "id" : server.id,
                    "ipv4" : server.ipv4,
                    "ipv6" : server.ipv6 if server.ipv6 != None else "",
                    "status" : 1 if status != False else 2,
                    "has_api" : True if server.api.public != None else False,
                    "registered" : server.added
                }
                
            self.show("main", servers=server_list)

    def post(self):
        server = int(self.get_argument("server", 0))
        act = self.get_argument("action", "")
        un = self.get_secure_cookie("un")

        keydb = json.loads(self.redis.get("%s_keys" % un))

        try:
            server_keys = keydb["%d" % server]
        except KeyError:
            self.write("2")
            self.finish()
            return
        
        if act == "update_status":
            ipv4 = self.get_argument("ipv4", "")
            ipv6 = self.get_argument("ipv6", "")

            status = 2

            if ipv4 != "" and server_keys['public'] != "":
                status = self.client(ipv4, msg="heartbeat", pub=server_keys['public'], priv=server_keys['private'])
            elif ipv4 == "" and server_keys['public'] != "" and ipv6 != "":
                status = self.client(ipv6, msg="heartbeat", ipv6=True, pub=server_keys['public'], priv=server_keys['private'])

            if status != False:
                self.write("1")
            else:
                self.write("0")
        elif act == "delete_server":
            print "server:",server
            
            if server != 0:
                done = None

                try:
                    done = self.db.servers.delete().where((self.db.servers.id==server) & (self.db.servers.user==self.uid)).execute()
                except:
                    self.db.database.rollback()

                if done != None:
                    keydb = json.loads(self.redis.get("%s_keys" % un))
                    del keydb["%d" % server]
                    self.redis.set("%s_keys" % un, json.dumps(keydb))
                    
                    self.write("1")
                else:
                    self.write("0")
        elif act == "edit_server":
            ipv4 = self.get_argument("ipv4", "")
            ipv6 = self.get_argument("ipv6", "")
            
            if server != 0:
                done = None

                try:
                    done = self.db.servers.update(ipv4=ipv4,ipv6=ipv6).where(self.db.servers.id==server).execute()
                except:
                    self.db.database.rollback()

                if done == 1:
                    self.write("1")
                else:
                    self.write("02")
            else:
                self.write("03")
        elif act == "update_server":
            if server != 0:
                done = None
                
                try:
                    done = self.db.jobqueue.create(server=server,ts=int(time()),cmd="update").get()
                except:
                    self.db.database.rollback()
                
                self.write(self.redis.get("cron_next_run"))
        elif act == "shutdown_server":
            if server != 0:
                server_info = self.db.servers.select(self.db.servers.ipv4).where(self.db.servers.id==server).get()
                self.client(server_info.ipv4, msg="shutdown", pub=server_keys['public'], priv=server_keys['private'])
        elif act == "cc":
            if server != 0:
                server_info = self.db.servers.select(self.db.servers.ipv4).where(self.db.servers.id==server).get()
                self.db.jobqueue.create(server=server,ts=int(time()),cmd="sysexec %s" % self.get_argument("cmd", ""))
                #except:
                #    self.db.database.rollback()
                
                self.write(self.redis.get("cron_next_run"))
        else:
            self.write("09999")

        self.finish()
