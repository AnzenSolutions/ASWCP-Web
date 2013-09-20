from plugins.bases.handlers import HandlersBase

import json

class reports(HandlersBase):
    WEB_PATH = r"/reports"
    STORE_ATTRS = True
    STORE_UNREF = True
    OPTS = {}

    def get(self):
        self.show("reports", msg="empty")
    
    def post(self):
        server = int(self.get_argument("server", 0))
        rid = int(self.get_argument("report_id", 0))
        act = str(self.get_argument("action", ""))
        
        if server != 0 and act != "":
            # Check to see if there's any new reports for server
            if act == "check_report":
                new_reports = 0
                
                new_reports = self.db.reports.select(self.db.reports.id).where((self.db.reports.unread == "t") & (self.db.reports.server == server)).count()
                
                if new_reports > 0:
                    self.write("%d|1" % server)
                else:
                    self.write("%d|0" % server)
                    
            # Fetch all unread reports for specified server
            elif act == "fetch_reports":
                the_reps = []
                
                reports = self.db.reports.select().where((self.db.reports.unread == True) & (self.db.reports.server == server)).order_by(self.db.reports.ts.desc()).dicts()
                    
                for report in reports.iterator():
                    the_reps.append(report)
                
                self.write(json.dumps(the_reps))
        
            # When user clicks to read report mark it as read
            elif act == "update_report":
                if rid != 0:
                    done = 0
                    
                    try:
                        done = self.db.reports.update(unread=False).where(self.db.reports.id==rid).execute()
                    except:
                        self.db.database.rollback()
                    
                    if done == 1:
                        self.write("1")
                    else:
                        self.write("0")
                        
        self.finish()
