from plugins.bases.handlers import HandlersBase

import json

from string import ascii_uppercase,ascii_lowercase,digits
from base64 import b64encode
import hashlib
import sha3
import random

class api(HandlersBase):
    WEB_PATH = r"/api"
    STORE_ATTRS = True
    STORE_UNREF = True
    OPTS = {}

    CSS_FILES = ["api"]
    JS_FILES = ["api"]

    def create_public_key(self, bits=2048):
        charlist = digits+ascii_uppercase+ascii_lowercase
        pairs = []

        char = ""

        for a in charlist:
            for b in charlist:
                char = ""
                char = a+b

                if char.lower() != a+b:
                    pairs.extend([char])

        return b64encode(hashlib.sha3_512(str(random.getrandbits(bits))).digest(), random.choice(pairs)).rstrip('==').replace("/","")

    def create_private_key(self, salt):
        from uuid import uuid4 as uid
        return b64encode(hashlib.sha3_512("%s%s" % (salt, uid())).digest()).rstrip('==').replace("/","")

    def get(self):
		un = self.get_secure_cookie("un")
		
		if not isinstance(un, basestring):
			self.redirect("/")
		else:		
			keys = json.loads(self.redis.get("%s_keys" % un))
			ref = self.request
			api_ref = "%s://%s" % (ref.protocol, ref.host)
			
			self.show("api", keys=keys, api_ref=api_ref)

    def post(self):
        act = self.get_argument("api_act", "")
        uid = int(self.get_secure_cookie("id"))
        un = self.get_secure_cookie("un")

        if act == "savek":
            pub = self.get_argument("pub", "")
            pri = self.get_argument("priv", "")
            server = int(self.get_argument("server", 0))

            if pub != "" and pri != "" and server != 0:
                created = None

                try:
                    created = self.db.api.create(private=pri,public=pub,server=server).get()
                except:
                    self.db.database.rollback()
                    self.write("e|Unable to store API key.  Had to roll back transaction.")
                    self.finish()

                if created != None:
                    serveri = self.db.servers.select(self.db.servers.hostname,self.db.servers.id).where(self.db.servers.id==server).limit(1).get()

                    keydb = json.loads(self.redis.get("%s_keys" % un))
                    keydb["%d" % serveri.id] = {"public" : pub, "private" : pri, "host" : serveri.hostname, "id" : created.id}
                    self.redis.set("%s_keys" % un, json.dumps(keydb))
                    self.write("s|Key has been saved to database!|%s|%d" % (serveri.hostname, created.id))
                else:
                    self.write("e|Unable to process API creation request.")
            else:
                self.write("e|Unable to save key information to server.  Make sure the server is also selected.")
        elif act == "deletek":
            server = 0

            try:
                server = int(self.get_argument("server", 0))
            except ValueError:
                pass

            kid = 0

            try:
                kid = int(self.get_argument("id", 0))
            except ValueError:
                pass

            if server != 0 and kid != 0:
                done = None

                try:
                    done = self.db.api.delete().where((self.db.api.id == kid) & (self.db.api.server == server)).execute()
                except:
                    self.db.database.rollback()

                if done == 1:
                    keydb = json.loads(self.redis.get("%s_keys" % un))

                    try:
                        del keydb["%d" % server]
                    except KeyError:
                        self.write("e|API key for server does not exist in system.")
                        self.finish()
                        return

                    self.redis.set("%s_keys" % un, json.dumps(keydb))
                    self.write("s|Key successfully deleted.")
                else:
                    self.write("e|Unable to delete key.  Does the key exist in the database?")
            else:
                self.write("e|Unable to delete key.  Improper data received.")
        elif act == "genk":
            bits = 0
            
            try:
                bits = int(self.get_argument("keybits", 0))
            except ValueError:
                pass

            # We need actual bit values and only ones that are a power of 2
            if bits > 0 and (bits & (bits-1)) == 0:
                self.write("s|%s" % self.create_api_key(bits))
            else:
                self.write("e|Either bits entered was 0 or was not a power of 2.")
        elif act == "genc":
            pub = self.create_public_key()
            priv = self.create_private_key(pub)
            ch = self.create_private_key("%s%s" % (pub, priv))

            self.redis.set(ch, "%s:%s:%s:%s"  % (pub, priv, self.get_secure_cookie("un"), self.uid ))

            self.write("s|%s" % ch)
        else:
            self.write("e|Unknown action.")
