from plugins.bases.handlers import HandlersBase

class forgotpassword(HandlersBase):
    WEB_PATH = r"/forgotpassword"
    STORE_ATTRS = True
    STORE_UNREF = True
    OPTS = {}
    
    PAGE_TITLE = "Reset Password"
    
    CSS_FILES = ["forgotpassword"]
    
    def get(self):
        self.show("forgotpassword", action="", msg_type="")

    def post(self):
        un = self.get_argument("user", "")
        email = self.get_argument("email", "")
        action = self.get_argument("action", "")
        
        if action == "":
            try:
                sql = self.db.users.get((self.db.users.username == un) & (self.db.users.email == email))
                self.show("forgotpassword", action="newpass", msg_type="", email=email)
            except:
                self.show("forgotpassword", msg_type="error", action="", msg="Invalid username and/or email provided.")
        elif action == "newpass":
            pw1 = self.get_argument("pw1", "")
            pw2 = self.get_argument("pw2", "")
            
            if (pw1 != "") and (pw2 != "") and (pw1 == pw2):
                pw = self.text2hash(pw1)
                
                if self.db.users.update(pw=pw).where(self.db.users.email == email).execute() == 1:
                    self.redirect("/login")
                else:
                    self.show("forgotpassword", msg_type="error", msg="Issue updating account's password.  Please try again.")
            else:
                self.show("forgotpassword", msg_type="error", msg="Passwords did not match or where left empty.  Please try again.")
        else:
            self.show("forgotpassword", msg_type="error", msg="Unknown action requested.")
