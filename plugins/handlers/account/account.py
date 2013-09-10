from plugins.bases.handlers import HandlersBase

import hashlib
import sha3

class account(HandlersBase):
    WEB_PATH = r"/account"
    STORE_ATTRS = True
    STORE_UNREF = True
    OPTS = {}

    PAGE_TITLE = "Account Management"

    def get(self):
        record = self.db.users.select(self.db.users.email).where(self.db.users.id==self.uid).get()

        self.show("account", msg="empty", msg_type="", email=record.email, cat=1)

    def post(self):
        action = self.get_argument("acct_act", "")
        curpw = self.text2hash(self.get_argument("curpw", ""))

        msg = ""
        msg_type = ""
        email = self.get_argument("email", "")
        alert_title = ""
        cat = 1

        if action == "changeemail":
            cat = 2

            new_email = self.get_argument("email", "")

            if new_email != "":
                done = None

                try:
                    done = self.db.users.update(email=new_email).where(
                        (self.db.users.id==self.uid) & 
                        (self.db.users.pw==curpw)).execute()
                except:
                    self.db.database.rollback()

                if done == 1:
                    msg = "The email has been updated."
                    msg_type = "success"
                    alert_title = "Success!"
                    email = new_email
                else:
                    msg = "Unable to update your email address.  Make sure you entered the correct password and the email address is different."
                    msg_type = "error"
                    alert_title = "Unable to change email!"
            else:
                msg = "Missing the current password or new email."
                msg_type = "error"
                alert_title = "Missing criteria!"
        elif action == "changepw":
            newpw1 = self.get_argument("newpw1", "")
            newpw2 = self.get_argument("newpw2", "")

            if newpw1 != "" and newpw2 != "" and newpw1 == newpw2:
                newpw = self.text2hash(newpw1)

                done = None

                try:
                    done = self.db.users.update(pw=newpw).where(
                        (self.db.users.id==self.uid) & 
                        (self.db.users.pw==curpw)).execute()
                except:
                    self.db.database.rollback()

                if done == 1:
                    msg = "Password change complete!"
                    msg_type = "success"
                    alert_title = "Password change successful!"
                else:
                    msg = "Unable to update password.  Please make sure the information provided is correct."
                    msg_type = "error"
                    alert_title = "Unable to change password!"
            else:
                msg = "Missing one or more criteria."
                msg_type = "error"
                alert_title = "Missing criteria!"

        if email == "":
            sql = self.db.users.select(self.db.users.email).where(self.db.users.id==self.uid).get()
            email = sql.email
            
        self.show("account", msg=msg, msg_type=msg_type, email=email, alert_title=alert_title, cat=cat)