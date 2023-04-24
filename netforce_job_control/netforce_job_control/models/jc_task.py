from netforce.model import Model, fields, get_model, clear_cache
from netforce.database import get_connection
import time
import datetime
from netforce.access import get_active_user,set_active_user
from netforce import access

class Task(Model):
    _name="jc.task"
    _string="Task"
    _multi_company=True
    _fields={
        "job_id": fields.Many2One("jc.job","Job",required=True,search=True,on_delete="cascade"),
        "contact_id": fields.Many2One("contact","Client",function="_get_related",function_context={"path":"job_id.contact_id"}),
        "service_id": fields.Many2One("jc.service","Service",function="_get_related",function_search="_search_related",function_context={"path":"job_id.service_id"}),
        "service_categ_id": fields.Many2One("jc.service.categ","Service Category",function="_get_related",function_search="_search_related",function_context={"path":"job_id.service_id.categ_id"}),
        "name": fields.Char("Task Name",required=True,search=True),
        "description": fields.Text("Description"),
        "deadline": fields.Date("Deadline",search=True),
        "state": fields.Selection([["in_progress","In Progress"],["done","Completed"],["waiting","Waiting"],["canceled","Canceled"]],"Task Status",required=True),
        "user_id": fields.Many2One("base.user","Assigned To",search=True),
        "documents": fields.One2Many("document","related_id","Documents"),
        "comments": fields.One2Many("message","related_id","Comments"),
        "overdue": fields.Boolean("Overdue",function="get_overdue",function_search="search_overdue"),
        "days_late": fields.Integer("Days Late",function="get_days_late"),
        "status_details": fields.Text("Status Details"),
        "wait_client": fields.Boolean("Wait For Client"),
        "last_fup": fields.Date("Last FUP"),
        "is_manager": fields.Boolean("Manager",store=False,function_search="search_is_manager"),
        "user_board": fields.Boolean("User",store=False,function_search="search_user_board"),
        "est_hours": fields.Decimal("Est. Hours"),
        "company_id": fields.Many2One("company","Company"),
    }
    _order="id"

    _defaults={
        "state": "in_progress",
        "company_id": lambda *a: access.get_active_company(),
    }

    def create(self,vals,**kw):
        new_id=super().create(vals,**kw)
        obj=self.browse(new_id)
        job=obj.job_id
        if obj.state in ("done","in_progress"):
            if obj.state=="done":
                s="Task '%s' completed"%obj.name
            elif obj.state=="in_progress":
                s="Task '%s' in progress"%obj.name
            get_model("jc.job.status").create({"job_id":obj.job_id.id,"description":s})
        return new_id

    def write(self,ids,vals,**kw):
        state=vals.get("state")
        if state in ("done","in_progress"):
            for obj in self.browse(ids):
                if state!=obj.state:
                    if state=="done":
                        s="Task '%s' completed"%obj.name
                    elif state=="in_progress":
                        s="Task '%s' in progress"%obj.name
                    get_model("jc.job.status").create({"job_id":obj.job_id.id,"description":s})
        super().write(ids,vals,**kw)
        for obj in self.browse(ids):
            job=obj.job_id
            if not job:
                continue
            job.update_tasks()
            clear_cache() # FIXME! 
            job.check_done()

    def delete(self,ids,**kw):
        job_ids=[]
        for obj in self.browse(ids):
            job_ids.append(obj.job_id.id)
        super().delete(ids,**kw)
        job_ids=list(set(job_ids))
        for job in get_model("jc.job").browse(job_ids):
            job.update_tasks()
            clear_cache() # FIXME! 
            job.check_done()

    def set_pending(self,ids,context={}):
        for obj in self.browse(ids):
            if obj.state!="draft":
                raise Exception("Invalid state")
            obj.write({"state":"pending"})

    def set_completed(self,ids,context={}):
        for obj in self.browse(ids):
            if obj.state not in ("draft","pending"):
                raise Exception("Invalid state")
            obj.write({"state":"done"})

    def set_draft(self,ids,context={}):
        for obj in self.browse(ids):
            if obj.state not in ("pending","completed"):
                raise Exception("Invalid state")
            obj.write({"state":"draft"})

    def get_overdue(self,ids,context={}):
        vals={}
        for obj in self.browse(ids):
            if obj.deadline:
                vals[obj.id]=obj.deadline<time.strftime("%Y-%m-%d") and obj.state!="done"
            else:
                vals[obj.id]=False
        return vals

    def search_overdue(self,clause,context={}):
        return [["deadline","<",time.strftime("%Y-%m-%d")],["state","!=","done"],["job_id.state","=","in_progress"]]

    def get_days_late(self,ids,context={}):
        vals={}
        d=datetime.datetime.now()
        for obj in self.browse(ids):
            if obj.deadline:
                vals[obj.id]=max(0,(d-datetime.datetime.strptime(obj.deadline,"%Y-%m-%d")).days) or None
            else:
                vals[obj.id]=None
        return vals

    def view_task(self,ids,context={}):
        obj=self.browse(ids[0])
        return {
            "next": {
                "name": "job",
                "mode": "form",
                "active_id": obj.job_id.id,
            }
        }

    def set_done(self,ids,context={}):
        print("task.set_done",ids)
        for obj in self.browse(ids):
            obj.write({"state":"done"})

    def search_is_manager(self,clause,context={}):
        user_id=get_active_user()
        return [["job_id.service_id.categ_id.manager_group_id.users.id","=",user_id]]

    def click_task(self,ids,context={}):
        task=self.browse(ids)[0]
        return {
            "next": {
                "name": "job",
                "active_id": task.job_id.id,
                "mode": "page",
            }
        }

    def search_user_board(self,clause,context={}):
        user_id=access.get_active_user()
        return ["user_id","=",user_id]

Task.register()
