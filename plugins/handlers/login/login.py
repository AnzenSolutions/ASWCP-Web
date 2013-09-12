from plugins.bases.handlers import HandlersBase

try:
	import json
except ImportError:
	import simplejson as json

class login(HandlersBase):
    WEB_PATH = r"/login"
    STORE_ATTRS = True
    STORE_UNREF = True
    OPTS = {}
    CSS_FILES = ["login"]

    PAGE_TITLE = "Login"

    def get(self):
    	if self.logged_in():
    		self.redirect("/")
    	else:
        	self.show("login", alert_title="Welcome to ASWCP!", msg="In order to manage your servers you need to log in.  If you can't remember your password you can <a href=\"/forgotpassword\">click here</a>.", msg_type="info")

    def post(self):
    	un = self.get_argument('user', "")
    	pw = self.get_argument('pass', "")

        if un != "" and pw != "":
            try:
                user = self.db.users.select(self.db.users.id).where(
                    (self.db.users.username == un) & (self.db.users.pw == self.text2hash(pw))
                ).limit(1).get()
            
                uid = user.id
            except:
                self.show("login", msg="Invalid username or password provided.", msg_type="error")
                self.finish()

            self.set_secure_cookie("id", str(uid))
            self.set_secure_cookie("un", str(un))

            apis = self.db.api.select(self.db.api).join(self.db.servers).where((self.db.servers.user==uid) & (self.db.api.server==self.db.servers.id))

            api_keys = {}

            for api in apis:
                api_keys["%d" % api.server.id] = {
                        "private" : api.private, "public" : api.public, "id" : api.id, "host" : api.server.hostname
                    }

            self.redis.set("%s_keys" % un, json.dumps(api_keys))

            self.redirect("/")
        else:
            self.show("login", msg="Missing one or more fields.", msg_type="error")
