from plugins.bases.handlers import HandlersBase

class forgotpassword(HandlersBase):
    WEB_PATH = r"/forgotpassword"
    STORE_ATTRS = True
    STORE_UNREF = True
    OPTS = {}

    CSS_FILES = ["forgotpassword"]

    def get(self):
        self.show("forgotpassword", msg_type="")

    def post(self):
    	un = self.get_argument("user", "")
    	email = self.get_argument("email", "")

    	if un != "" and email != "":
    		sql = self.db.select("id").on("users").where("username = '%s'" % un).where("email = '%s'" % email).results

    		if len(sql) == 1:
    			self.show("login", alert_title="Password Changed", msg_type="success", msg="Please check your email for your new password.")
    		else:
    			self.show("forgotpassword", msg_type="error", msg="Invalid username and/or email provided.")
    	else:
    		self.show("forgotpassword", alert_title="Missing Information!", msg_type="error", msg="No username or email provided.")
