from plugins.bases.handlers import HandlersBase

from time import time
import hashlib
import json

class server(HandlersBase):
    WEB_PATH = r"/server/(.*)"
    STORE_ATTRS = True
    STORE_UNREF = True
    OPTS = {}

    JS_FILES = ["server_add"]

    def get(self, act):
        if act != "":
            self.show("server_%s" % act, msg="empty")
        else:
            self.redirect("/")

    def post(self, act):
        if act == "add":
            challenge = self.get_argument("challenge", "")

            if challenge == "":
                self.write("e|No challenge string provided.")
                return None

            try:
                pub,priv,_,_ = str(self.redis.get(challenge)).split(":")
                kp = "%s:%s" % (pub, priv)
            except:
                self.write("e|Unable to retrieve key pair by challenge string.  Is it correct?")
                return None

            self.write("%s" % kp)
        elif act == "done":
            resp = self.get_argument("info", "")
            ch = self.get_argument("challenge", "")

            if resp == "" or ch == "":
                self.write("e|No server information provided.")
                return None

            stat,host,ip = resp.split("|")

            if stat == "" or host == "" or ip == "":
                self.write("e|One or more fields were missing.")
                return None

            try:
                ipv,ipa = ip.split(",")
            except:
                self.write("e|Missing either IP version or address.")
                return None

            if ipv != "4" and ipv != "6":
                self.write("e|Invalid IP version.")
                return None

            ipv = int(ipv)

            created = None

            pub,priv,un,uid = str(self.redis.get(ch)).split(":")
            
            if ipv == 4:
                try:
                    created = self.db.servers.get((self.db.servers.ipv4 == ipa) & (self.db.servers.hostname == host) & (self.db.servers.user == uid))
                except:
                    created = self.db.servers.create(user=uid,ipv4=ipa,hostname=host,added=time())
            else:
                try:
                    created = self.db.servers.get(self.db.servers.ipv6 == ipa & self.db.servers.hostname == host & self.db.servers.user == uid)
                except:
                    created = self.db.servers.create(user=uid,ipv6=ipa,hostname=host,added=time())
                    
            # except:
            #    self.db.database.rollback()
            
            if created.id != None:
                apic = None

                try:
                    apic = self.db.api.create(private=priv, public=pub, server=created.id)
                except:
                    self.db.database.rollback()
                    self.write("e|Unable to save API key.")
                    return None

                if apic != None:
                    keydb = json.loads(self.redis.get("%s_keys" % un ))
                    keydb["%d" % created.id] = {"public" : pub, "private" : priv, "host" : host, "id" : apic.id}
                    self.redis.set("%s_keys" % un, json.dumps(keydb))
                    self.write("s|Keys saved to database.")
                    self.redis.delete(ch)
            else:
                self.write("e|Unable to create server entry in database.")
                return None
        elif act == "update":
            print "hi"

        self.finish()
