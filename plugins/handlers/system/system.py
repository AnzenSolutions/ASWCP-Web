from plugins.bases.handlers import HandlersBase

class system(HandlersBase):
    WEB_PATH = r"/system"
    STORE_ATTRS = True
    STORE_UNREF = True
    OPTS = {}
    
    PAGE_TITLE = "Sytem Information"
    
    def get(self):
        self.show("system", conf=self.sysconf.__dict__)
    
    def post(self):
        act = self.get_request("act", "")
        
        if act == "edit_conf":
            self.write("0|Unable to edit config, feature not enabled.")
        else:
            self.write("-1|Unknown action")
        
        self.finish()
