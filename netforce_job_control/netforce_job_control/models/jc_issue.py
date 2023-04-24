from netforce.model import Model, fields
import time
from netforce import access
import datetime

class Issue(Model):
    _name="jc.issue"
    _string="Issue"
    _fields={
        "date": fields.DateTime("Date Created",required=True,search=True),
        "name": fields.Char("Subject",required=True,search=True),
        "report_by_id": fields.Many2One("base.user","Reported By",search=True),
        "assigned_to_id": fields.Many2One("base.user","Assigned To",search=True),
        "details": fields.Text("Details",search=True),
        "state": fields.Selection([["open","Open"],["closed","Closed"]],"Status",required=True),
        "attach": fields.File("Attachment"),
        "priority": fields.Selection([["low","Low"],["normal","Normal"],["high","High"]],"Priority",search=True),
        "comments": fields.One2Many("message","related_id","Comments"),
        "overdue": fields.Boolean("Overdue",function="get_overdue",function_search="search_overdue"),
    }
    _order="date desc"

    _defaults={
        "state": "open",
        "date": lambda *a: time.strftime("%Y-%m-%d %H:%M:%S"),
        "report_by_id": lambda *a: access.get_active_user(),
        "priority": "normal",
    }

    def create(self,vals,**kw):
        new_id=super().create(vals,**kw)
        assign_ids=[]
        assigned_to_id=vals.get("assigned_to_id")
        if assigned_to_id:
            assign_ids.append(new_id)
        if assign_ids:
            self.trigger(assign_ids,"assigned")
        return new_id

    def write(self,ids,vals,**kw):
        event=None
        assign_ids=[]
        assigned_to_id=vals.get("assigned_to_id")
        state=vals.get("state")
        event_helper={
            "closed":"closed",
            "open":"reopened"
        }
        if assigned_to_id:
            assign_ids+=ids
            event="assigned"
        elif state:
            assign_ids+=ids
            event=event_helper[state]
        super().write(ids,vals,**kw)
        if assign_ids:
            self.trigger(assign_ids,event)

    def check_days_old(self,ids,days_from=None,days_to=None,priority=None,context={}):
        print("Issue.check_days_old",ids,days_from,days_to)
        dom=[["state","!=","closed"]]
        if days_from!=None:
            d=(datetime.date.today()-datetime.timedelta(days=days_from)).strftime("%Y-%m-%d 00:00:00")
            dom.append(["date","<=",d])
        if days_to!=None:
            d=(datetime.date.today()-datetime.timedelta(days=days_to)).strftime("%Y-%m-%d 00:00:00")
            dom.append(["date",">=",d])
        if priority!=None:
            dom.append(["priority","=",priority])
        if ids:
            dom.append(["ids","in",ids])
        ids=self.search(dom)
        return ids

    def get_overdue(self,ids,context={}):
        vals={}
        for obj in self.browse(ids):
            vals[obj.id]=obj.state=="open" and obj.date<(datetime.datetime.now()-datetime.timedelta(days=2)).strftime("%Y-%m-%d %H:%M:%S")
        return vals

    def search_overdue(self,clause,context={}):
        date_from=(datetime.datetime.now()-datetime.timedelta(days=2)).strftime("%Y-%m-%d %H:%M:%S")
        return [["date","<",date_from],["state","=","open"]]

Issue.register()
