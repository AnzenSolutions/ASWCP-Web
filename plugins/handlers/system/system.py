from plugins.bases.handlers import HandlersBase

class system(HandlersBase):
    WEB_PATH = r"/system"
    STORE_ATTRS = True
    STORE_UNREF = True
    OPTS = {}
    
    PAGE_TITLE = "Sytem Information"
    
    def get(self):
        self.show("system", conf=self.sysconf.__dict__)
