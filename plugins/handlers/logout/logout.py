from plugins.bases.handlers import HandlersBase

class logout(HandlersBase):
    WEB_PATH = r"/logout"
    STORE_ATTRS = True
    STORE_UNREF = True
    OPTS = {}

    def get(self):
        if self.logged_in():
        	self.redis.delete("%s_keys" % self.get_un)
        	self.clear_all_cookies()

        self.redirect("/login")
