from plugins.bases.handlers import HandlersBase

class install(HandlersBase):
    WEB_PATH = r"/install"
    STORE_ATTRS = True
    STORE_UNREF = True
    OPTS = {}

    def get(self):
        self.show("install", msg="empty", show_menu=False)
