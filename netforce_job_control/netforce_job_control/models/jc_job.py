from netforce.model import Model, fields, get_model
from netforce.access import get_active_user,set_active_user
import datetime
import time
from dateutil.relativedelta import relativedelta
from netforce.database import get_connection
from netforce.access import get_active_company
from netforce import access
from netforce import tasks
from decimal import *
import requests

def rpc_exec(model,method,args=[],opts={}):
    print("rpc_exec",model,method,args,opts)
    headers={
        "Cookie": "user_id=1; package=enterprise; user_name=admin; dbname=antares; company_id=1; company_name=Antares%20Group; token=YW50YXJlcyAx%7C1544453434%7Cc604d17d757b9dae9e9629a3a1076b2cd47562ab", # XXX
    }
    data={
        "id": int(time.time()),
        "method": "execute",
        "params": [
            model,
            method,
            args,
            opts,
        ],
    }
    url="http://admin.myantares.com/json_rpc"
    req=requests.post(url,json=data,headers=headers)
    res=req.json()
    if res.get("error"):
        raise Exception(res["error"])
    return res["result"]

class Job(Model):
    _name="jc.job"
    _string="Job"
    _name_field="number"
    _audit_log=True
    _multi_company=True
    _fields={
        "contact_id": fields.Many2One("contact","Client",required=True,search=True),
        "person_id": fields.Many2One("contact","Contact Person"),
        "template_id": fields.Many2One("jc.job.template","Template"),
        "service_id": fields.Many2One("jc.service","Service (DEPRECATED)"), # XXX: dreprecated
        "product_id": fields.Many2One("product","Service Product",condition=[["type","=","service"]]),
        "service_categ_id": fields.Many2One("jc.service.categ","Service Category",function="_get_related",function_search="_search_related",function_context={"path":"service_id.categ_id"}),
        "name": fields.Char("Job Name",required=True,search=True),
        "number": fields.Char("Job Number",required=True,search=True),
        "description": fields.Text("Description"),
        "start_date": fields.Date("Start Date"),
        "due_date": fields.Date("Due Date",search=True,required=True),
        "priority": fields.Selection([["low","Low"],["medium","Medium"],["high","High"]],"Priority"),
        "state": fields.Selection([["in_progress","In Progress"],["done","Completed"],["verified","Verified"],["invoiced","Invoiced"],["canceled","Canceled"]],"Job Status",required=True),
        "overdue": fields.Boolean("Overdue",function="get_overdue",function_search="search_overdue"),
        "comments": fields.One2Many("message","related_id","Comments"),
        "documents": fields.One2Many("document","related_id","Documents"),
        "folders": fields.One2Many("folder","related_id","Folders"),
        "folder_id": fields.Many2One("folder","Folder"),
        "tasks": fields.One2Many("jc.task","job_id","Tasks"),
        "time_entries": fields.One2Many("time.entry","jc_job_id","Time Entries"),
        "time_entries_invoiced": fields.One2Many("time.entry","jc_job_id","Invoiced Time Entries",condition=[["state","=","invoiced"]]),
        "time_entries_other": fields.One2Many("time.entry","jc_job_id","Time Entries",condition=[["state","!=","invoiced"],["state","!=","merged"]]),
        "time_entries_approved": fields.One2Many("time.entry","jc_job_id","Approved Time Entries",condition=[["state","=","approved"]]),
        "time_entries_merged": fields.One2Many("time.entry","jc_job_id","Merged Time Entries",condition=[["state","=","merged"]]),
        "num_tasks": fields.Integer("# Tasks",function="get_num_tasks"),
        "days_late": fields.Integer("Days Late",function="get_days_late"),
        "user_id": fields.Many2One("base.user","Assigned To",search=True),
        "request_by_id": fields.Many2One("base.user","Requested By",search=True),
        "user_board": fields.Boolean("User",store=False,function_search="search_user_board"),
        "current_work": fields.Text("Status Details",function="get_current_work",function_multi=True),
        "last_fup": fields.Date("Last FUP",function="get_current_work",function_multi=True),
        "invoice_no": fields.Char("Invoice No."), # XXX: not used any more...
        "required_docs": fields.One2Many("jc.required.doc","related_id","Required Documents"),
        "shared_board": fields.Boolean("Shared",store=False,function_search="search_shared_board"),
        "is_manager": fields.Boolean("Manager",store=False,function_search="search_is_manager"),
        "status_history": fields.One2Many("jc.job.status","job_id","Status History"),
        "quotation_id": fields.Many2One("sale.quot","Quotation"),
        "cancel_reason": fields.Text("Cancel Reason"),
        "cancel_periodic": fields.Boolean("Cancel Periodic"),
        "next_job_id": fields.Many2One("jc.job","Next Job"),
        "emails": fields.One2Many("email.message","related_id","Emails"),
        "company_id": fields.Many2One("company","Company"),
        "invoices": fields.One2Many("account.invoice","related_id","Invoices"),
        "payments": fields.One2Many("account.payment","related_id","Payments"),
        "bill_amount": fields.Float("Billable Amount",required=True),
        "percent_invoiced": fields.Integer("% Invoiced",function="_get_paid",function_multi=True),
        "percent_paid": fields.Integer("% Paid",function="_get_paid",function_multi=True),
        "deposit_amount": fields.Float("Deposit Amount"),
        "invoice_id": fields.Many2One("account.invoice","Invoice"),
        "is_duplicate": fields.Boolean("Duplicate"),
        "users": fields.Many2Many("base.user","Other Involved Users"),
        "percent_done": fields.Integer("% Completed",function="get_percent_done"),
        "budget_hours": fields.Decimal("Budget Hours"),
        "involved_user_id": fields.Many2One("base.user","Search Involved User",store=False,function_search="search_involved_user"),
        "bill_type": fields.Selection([["hour","Hourly"],["flat","Flat Fee"]],"Billing Type"),
        "uninvoiced_time_amount": fields.Decimal("Uninvoiced Time Entries",function="get_uninvoiced_amount"),
        "uninvoiced_hours": fields.Decimal("Uninvoiced Hours",function="get_uninvoiced_hours"),
        "approved_time_amount": fields.Decimal("Approved Time Entries",function="get_approved_amount"),
        "approved_hours": fields.Decimal("Approved Hours",function="get_approved_hours"),
        "total_bill_hours": fields.Decimal("Total Bill Hours",function="get_time_total",function_multi=True),
        "total_bill_amount": fields.Decimal("Total Bill Amount",function="get_time_total",function_multi=True),
        "time_users": fields.Many2Many("base.user","Time Entry Users",function="get_time_users"),
        "time_users_preview": fields.Many2Many("base.user","Time Entry Users",function="get_time_users_preview"),
        "est_hours": fields.Decimal("Est Hours"),
        "payment_plans": fields.One2Many("payment.plan","related_id","Payment Installments"),
        "expenses": fields.One2Many("expense","related_id","Expenses"),
        "invoiced_expenses": fields.One2Many("expense","related_id","Invoiced Expenses",condition=[["invoice_id","!=",None]]),
    }
    _order="start_date desc"
    _sql_constraints=[
        ("number_uniq","unique (number)","The job number must be unique!"),
    ]

    def _get_number(self, context={}):
        seq_id = get_model("sequence").find_sequence(model="jc.job",context=context)
        if not seq_id:
            raise Exception("Missing number sequence")
        while 1:
            num = get_model("sequence").get_next_number(seq_id, context=context)
            if not num:
                return None
            user_id = access.get_active_user()
            access.set_active_user(1)
            res = self.search([["number", "=", num]])
            access.set_active_user(user_id)
            if not res:
                return num
            get_model("sequence").increment_number(seq_id, context=context)

    def name_get(self,ids,context={}):
        vals=[]
        for obj in self.browse(ids):
            name=obj.contact_id.name
            if obj.name:
                name+=" - "+obj.name
            vals.append((obj.id,name))
        return vals

    def name_search(self, name, condition=None, context={}, limit=None, order=None, **kw):
        cond=["or",["name","ilike",name],["contact_id.name","ilike",name]]
        if condition:
            cond=[cond,condition]
        ids = self.search(cond, limit=limit, order=order)
        return self.name_get(ids, context=context)

    _defaults={
        "state": "in_progress",
        "number": _get_number,
        "start_date": lambda *a: time.strftime("%Y-%m-%d"),
        "request_by_id": lambda *a: get_active_user(),
        "company_id": lambda *a: access.get_active_company(),
    }

    _constraints=["check_state"]

    def check_state(self,ids,context={}):
        return # XXX
        for obj in self.browse(ids):
            if obj.state in ("done","verified","invoiced"):
                for task in obj.tasks:
                    if task.state!="done":
                        raise Exception("Invalid job status, some tasks are not completed")
            #elif obj.state=="canceled":
            #    for task in obj.tasks:
            #        if task.state in ("in_progress","waiting"):
            #            raise Exception("Invalid job status, some tasks are still in progress")

    def create(self,vals,**kw):
        new_id=super().create(vals,**kw)
        self.create_tasks([new_id])
        self.create_folder([new_id])
        return new_id


    def write(self,ids,vals,context={},**kw):
        state=vals.get("state")
        raise Exception("debgging 2")
        if state=="done" and not context.get("set_done"):
            raise Exception("Please use the \"Completed\" button to complete the job.")
        done_ids=[]
        if state=="done":
            for obj in self.browse(ids):
                if obj.state!="done": # XXX: not needed after fix UI
                    done_ids.append(obj.id)
        if state:
            for obj in self.browse(ids):
                if obj.state!=state:
                    if state=="in_progress":
                        s="Job in progress"
                    elif state=="done":
                        s="Job completed"
                    elif state=="verified":
                        s="Job verified"
                    elif state=="invoiced":
                        s="Job invoiced"
                    elif state=="canceled":
                        s="Job canceled"
                    get_model("jc.job.status").create({"job_id":obj.id,"description":s})
        assign_ids=[]
        user_id=vals.get("user_id")
        if user_id:
            for obj in self.browse(ids):
                if obj.user_id.id!=user_id: # XXX: not needed after fix UI
                    assign_ids.append(obj.id)
        super().write(ids,vals,context=context,**kw)
        if done_ids:
            self.trigger(done_ids,"completed")
        if assign_ids:
            self.trigger(assign_ids,"assigned")
        self.create_folder(ids)

    def set_done(self,ids,context={}):
        obj=self.browse(ids[0])
        obj.write({"state":"done"},context={"set_done":True})

    def get_overdue(self,ids,context={}):
        vals={}
        for obj in self.browse(ids):
            if obj.due_date:
                vals[obj.id]=obj.due_date<time.strftime("%Y-%m-%d") and obj.state=="in_progress"
            else:
                vals[obj.id]=False
        return vals

    def search_overdue(self,clause,context={}):
        return [["due_date","<",time.strftime("%Y-%m-%d")],["state","=","in_progress"]]

    def get_days_late(self,ids,context={}):
        vals={}
        d=datetime.datetime.now()
        for obj in self.browse(ids):
            if obj.due_date:
                vals[obj.id]=(d-datetime.datetime.strptime(obj.due_date,"%Y-%m-%d")).days
            else:
                vals[obj.id]=None
        return vals

    def onchange_product(self,context={}):
        data=context["data"]
        prod_id=data["product_id"]
        if not prod_id:
            return
        prod=get_model("product").browse(prod_id)
        data["name"]=prod.name
        data["number"]=self._get_number()
        uom=prod.uom_id
        if uom.name.lower()=="hour":
            data["bill_type"]="hour"
        else:
            data["bill_type"]="flat"
        data["bill_amount"]=prod.sale_price
        data["est_hours"]=prod.est_hours
        res=get_model("jc.job.template").search([["product_id","=",prod_id]])
        if res:
            tmpl_id=res[0]
            data["template_id"]=tmpl_id
            data=self.onchange_template(context=context)
        return data

    def onchange_template(self,context={}):
        data=context["data"]
        template_id=data["template_id"]
        if not template_id:
            return
        tmpl=get_model("jc.job.template").browse(template_id)
        date=time.strftime("%Y-%m-%d")
        ctx={
            "Y": date[0:4],
            "y": date[2:4],
            "m": date[5:7],
            "d": date[8:10],
        }
        job_name=tmpl.job_name%ctx
        data.update({
            "product_id": tmpl.product_id.id,
            "number": self._get_number(),
            "name": job_name,
            "description": tmpl.description,
        })
        contact_id=data.get("contact_id")
        if tmpl.assign_from_client and contact_id:
            contact=get_model("contact").browse(contact_id)
            data["user_id"]=contact.assigned_to_id.id
        if tmpl.due_date:
            if tmpl.due_date.startswith("+"):
                days=int(tmpl.due_date[1:])
                d=(datetime.date.today()+datetime.timedelta(days=days)).strftime("%Y-%m-%d")
            elif tmpl.due_date[2]=="-":
                d=time.strftime("%Y-")+tmpl.due_date
            else:
                d=time.strftime("%Y-%m-")+tmpl.due_date
            data["due_date"]=d
        return data

    def confirm(self,ids,context={}):
        obj=self.browse(ids)[0]
        if obj.state!="new":
            raise Exception("Can only confirm jobs in 'Not Started' state")
        if obj.template_id:
            obj.create_tasks()
        obj.write({"state":"in_progress"})

    def create_tasks(self,ids,context={}):
        print("job.create_tasks",ids)
        obj=self.browse(ids)[0]
        tmpl=obj.template_id
        if not tmpl:
            return {
                "flash": "No template defined for this job",
            }
        tasks={}
        done_tasks=set()
        for task in obj.tasks:
            tasks[task.name]=task
            if task.state=="done":
                done_tasks.add(task.name)
        task_names={}
        for task in tmpl.task_templates:
            task_names[task.sequence]=task.name
        count=0
        for task in tmpl.task_templates:
            if task.name in tasks:
                continue
            state="in_progress"
            if task.wait_for:
                wait_for=set([task_names[int(s.strip())] for s in task.wait_for.split(",")])
                if not wait_for.issubset(done_tasks):
                    state="waiting"
            vals={
                "job_id": obj.id,
                "name": task.name,
                "description": task.description,
                "user_id": task.user_id.id,
                "state": state,
            }
            if task.assign_from_job:
                vals["user_id"]=obj.user_id.id
            if task.deadline:
                if task.deadline.startswith("+"):
                    if task.wait_for:
                        d=None
                    else:
                        days=int(task.deadline[1:])
                        d=(datetime.date.today()+datetime.timedelta(days=days)).strftime("%Y-%m-%d")
                elif task.deadline.startswith("-"):
                    days=int(task.deadline[1:])
                    due_d=datetime.strptime(obj.due_date,"%Y-%m-%d")
                    d=(due_d-datetime.timedelta(days=days)).strftime("%Y-%m-%d")
                else:
                    d=time.strftime("%Y-%m-")+task.deadline
                vals["deadline"]=d
            task_id=get_model("jc.task").create(vals)
            count+=1
        #obj.create_required_docs()
        return {
            "flash": "%d tasks created"%count,
        }

    def create_required_docs(self,ids,context={}):
        print("job.create_required_docs",ids)
        obj=self.browse(ids)[0]
        tmpl=obj.template_id
        for doc in tmpl.required_docs:
            vals={
                "name": doc.name,
                "related_id": "job,%s"%obj.id,
            }
            get_model("required.doc").create(vals)

    def update_tasks(self,ids,context={}):
        print("job.update_tasks",ids)
        obj=self.browse(ids)[0]
        tmpl=obj.template_id
        if not tmpl:
            return
        pending_tasks=set()
        for task in obj.tasks:
            if task.state!="done":
                pending_tasks.add(task.name)
        task_names={}
        task_tmpls={}
        for task in tmpl.task_templates:
            task_names[task.sequence]=task.name
            task_tmpls[task.name]=task
        for task in obj.tasks:
            if task.state!="waiting":
                continue
            tmpl=task_tmpls.get(task.name)
            if tmpl and tmpl.wait_for:
                wait_for=set([task_names[int(s.strip())] for s in tmpl.wait_for.split(",")])
                if not wait_for.intersection(pending_tasks):
                    task.write({"state":"in_progress"})
                    if tmpl.deadline:
                        if tmpl.deadline.startswith("+"):
                            days=int(tmpl.deadline[1:])
                            d=(datetime.date.today()+datetime.timedelta(days=days)).strftime("%Y-%m-%d")
                            task.write({"deadline":d})

    def check_done(self,ids,context={}):
        print("job.check_done",ids)
        obj=self.browse(ids)[0]
        tmpl=obj.template_id
        if not tmpl:
            return
        if not tmpl.auto_complete:
            return
        for task in obj.tasks:
            if task.state!="done":
                return
        user_id=get_active_user()
        set_active_user(1)
        obj.write({"state":"done"})
        set_active_user(user_id)

    def get_num_tasks(self,ids,context={}):
        vals={}
        for obj in self.browse(ids):
            vals[obj.id]=len(obj.tasks)
        return vals

    def batch_create(self,context={}):
        count=0
        for tmpl in get_model("job.template").search_browse([]):
            if tmpl.create_when=="never":
                continue
            for contact in get_model("contact").search_browse([["job_templates.id","=",tmpl.id]]):
                if tmpl.service_id.id not in [s.id for s in contact.services]:
                    continue
                vals={
                    "template_id": tmpl.id,
                    "contact_id": contact.id,
                    "service_id": tmpl.service_id.id,
                    "name": tmpl.job_name,
                    "description": tmpl.description,
                }
                if tmpl.due_date:
                    if tmpl.due_date.startswith("+"):
                        days=int(tmpl.due_date[1:])
                        d=(datetime.date.today()+datetime.timedelta(days=days)).strftime("%Y-%m-%d")
                    else:
                        d=time.strftime("%Y-%m-")+tmpl.due_date
                    vals["due_date"]=d
                res=self.search([["contact_id","=",vals["contact_id"]],["name","=",vals["name"]]],limit=1,order="start_date desc")
                if res:
                    last_job=self.browse(res[0])
                    d=time.strftime("%Y-%m-%d")
                    if tmpl.create_when=="month":
                        if last_job.start_date[:7]==d[:7]:
                            continue
                    elif tmpl.create_when=="half_year":
                        continue # XXX
                    elif tmpl.create_when=="year":
                        continue # XXX
                job_id=self.create(vals)
                count+=1
        return {
            "next": {
                "name": "jc_job",
            },
            "flash": "%d jobs created"%count,
        }

    def get_days_late(self,ids,context={}):
        vals={}
        d=datetime.datetime.now()
        for obj in self.browse(ids):
            if obj.due_date:
                vals[obj.id]=max(0,(d-datetime.datetime.strptime(obj.due_date,"%Y-%m-%d")).days) or None
            else:
                vals[obj.id]=None
        return vals

    def search_user_board(self,clause,context={}):
        user_id=access.get_active_user()
        return ["or",["user_id","=",user_id],["users.id","=",user_id]]

    def get_current_work(self,ids,context={}):
        stat_ids=get_model("jc.job.status").search([["job_id","in",ids]],order="date,id")
        job_stats={}
        job_dates={}
        for stat in get_model("jc.job.status").browse(stat_ids):
            job_stats[stat.job_id.id]=stat.description
            job_dates[stat.job_id.id]=stat.date
        vals={}
        for obj in self.browse(ids):
            vals[obj.id]={
                "current_work": job_stats.get(obj.id),
                "last_fup": job_dates.get(obj.id),
            }
        return vals

    def search_shared_board(self,clause,context={}):
        user_id=get_active_user()
        pending_job_ids=self.search([["state","=","in_progress"]])
        share_ids=get_model("share.record").search([["user_id","=",user_id],["related_id","in",["job,%s"%job_id for job_id in pending_job_ids]]])
        res=get_model("share.record").read(share_ids,["related_id"])
        job_ids=[]
        for r in res:
            job_id=int(r["related_id"][0].split(",")[1])
            job_ids.append(job_id)
        return [["id","in",job_ids]]

    def search_is_manager(self,clause,context={}):
        user_id=get_active_user()
        return [["service_id.categ_id.manager_group_id.users.id","=",user_id]]

    def create_periodic_jobs(self,context={}):
        print("***************************************************************")
        print("create_periodic_job")
        for period in ("month","year"):
            if period=="month":
                date=(datetime.date.today()-relativedelta(months=1)).strftime("%Y-%m-%d")
            elif period=="year":
                date=(datetime.date.today()-relativedelta(years=1)).strftime("%Y-%m-%d")
            res=self.search([["start_date","=",date],["template_id.periodicity","=",period],["next_job_id","=",None]])
            for obj in self.browse(res):
                obj.create_next()

    def create_next(self,ids,context={}):
        print("Job.create_next",ids)
        obj=self.browse(ids)[0]
        if obj.next_job_id:
            raise Exception("Next job is already created")
        tmpl=obj.template_id
        period=tmpl.periodicity
        if not period:
            raise Exception("Job is not periodic")
        if not obj.start_date:
            raise Exception("No start date")
        if obj.state=="canceled" and obj.cancel_periodic:
            return
        due_date=None
        if period=="month":
            start_date=(datetime.datetime.strptime(obj.start_date,"%Y-%m-%d")+relativedelta(months=1)).strftime("%Y-%m-%d")
            if obj.due_date:
                due_date=(datetime.datetime.strptime(obj.due_date,"%Y-%m-%d")+relativedelta(months=1)).strftime("%Y-%m-%d")
        elif period=="year":
            start_date=(datetime.datetime.strptime(obj.start_date,"%Y-%m-%d")+relativedelta(years=1)).strftime("%Y-%m-%d")
            if obj.due_date:
                due_date=(datetime.datetime.strptime(obj.due_date,"%Y-%m-%d")+relativedelta(years=1)).strftime("%Y-%m-%d")
        ctx={
            "Y": start_date[0:4],
            "y": start_date[2:4],
            "m": start_date[5:7],
            "d": start_date[8:10],
        }
        job_name=tmpl.job_name%ctx
        vals={
            "contact_id": obj.contact_id.id,
            "person_id": obj.person_id.id,
            "template_id": tmpl.id,
            "service_id": obj.service_id.id,
            "name": job_name,
            "number": self._get_number(context={"categ_id":obj.service_id.categ_id.id}),
            "start_date": start_date,
            "due_date": due_date,
            "user_id": obj.user_id.id,
            "request_by_id": obj.request_by_id.id,
        }
        new_id=self.create(vals)
        obj.write({"next_job_id":new_id})
        return {
            "next": {
                "name": "job",
                "mode": "page",
                "active_id": new_id,
            },
            "flash": "Job created successfully",
        }

    def check_days_before_overdue(self,ids,days=None,days_from=None,days_to=None,context={}):
        print("Job.check_days_before_overdue",ids,days)
        dom=[["state","=","in_progress"]]
        if days!=None:
            d=(datetime.date.today()+datetime.timedelta(days=days)).strftime("%Y-%m-%d")
            dom.append(["due_date","=",d])
        if days_from!=None:
            d=(datetime.date.today()+datetime.timedelta(days=days_from)).strftime("%Y-%m-%d")
            dom.append(["due_date","<=",d])
        if days_to!=None:
            d=(datetime.date.today()+datetime.timedelta(days=days_to)).strftime("%Y-%m-%d")
            dom.append(["due_date",">=",d])
        if ids:
            dom.append(["ids","in",ids])
        ids=self.search(dom)
        return ids

    def _get_paid(self,ids,context={}):
        user_id=get_active_user()
        try:
            set_active_user(1)
            vals={}
            for obj in self.browse(ids):
                #amt_total=0
                amt_invoiced=0
                amt_paid=0
                amt_total=obj.bill_amount or 0
                #amt_total=get_model("currency").round(1,amt_total*1.07) # FIXME
                if obj.invoice_id: # XXX: improve this
                    invoices=[obj.invoice_id]
                else:
                    invoices=obj.invoices
                for inv in invoices:
                    if inv.state in ("waiting_payment","paid"):
                        amt_invoiced+=inv.amount_total
                        amt_paid+=inv.amount_paid
                for pmt in obj.payments:
                    if pmt.state=="posted":
                        amt_paid+=pmt.amount_total
                if amt_total:
                    percent_invoiced=round(amt_invoiced*100/Decimal(amt_total))
                    percent_paid=round(amt_paid*100/Decimal(amt_total))
                else:
                    percent_invoiced=0
                    percent_paid=0
                vals[obj.id]={
                    "percent_invoiced": percent_invoiced,
                    "percent_paid": percent_paid,
                }
        finally:
            set_active_user(user_id)
        return vals

    def copy_to_invoice(self,ids,context={}):
        id=ids[0]
        obj=self.browse(id)
        inv_vals={
            "type": "out",
            "inv_type": "invoice",
            "ref": obj.number,
            "related_id": "job,%s"%obj.id,
            "contact_id": obj.contact_id.id,
            "lines": [],
        }
        prod=obj.service_id.product_id
        if not prod:
            raise Exception("No product configured for service %s"%obj.service_id.name)
        line_vals={
            "product_id": prod.id,
            "description": prod.description,
            "qty": 1,
            "uom_id": prod.uom_id.id,
            "unit_price": prod.sale_price,
            "account_id": prod and prod.sale_account_id.id or None,
            "tax_id": prod.sale_tax_id.id,
        }
        inv_vals["lines"].append(("create",line_vals))
        inv_id=get_model("account.invoice").create(inv_vals,{"type":"out","inv_type":"invoice"})
        inv=get_model("account.invoice").browse(inv_id)
        obj.write({"invoice_id":inv_id})
        return {
            "next": {
                "name": "cust_invoice_edit",
                "active_id": inv_id,
            },
            "flash": "Invoice %s created from job %s"%(inv.number,obj.number),
            "invoice_id": inv_id,
        }

    def check_dup(self,context={}):
        print("check_dup")
        prev_job=None
        num_dups=0
        for obj in self.search_browse([["state","=","in_progress"],["template_id","!=",None]],order="contact_id,template_id,start_date,name,id"):
            print(obj.contact_id.name,obj.template_id.name,obj.id)
            tmpl=obj.template_id
            if tmpl.periodicity not in ("month","year"):
                continue
            if prev_job and obj.contact_id.id==prev_job.contact_id.id and obj.template_id.id==prev_job.template_id.id and (datetime.datetime.strptime(obj.start_date,"%Y-%m-%d")-datetime.datetime.strptime(prev_job.start_date,"%Y-%m-%d")).days<=20 and obj.name==prev_job.name: # XXX
                print("DUP")
                obj.write({"is_duplicate":True})
                num_dups+=1
            prev_job=obj
        print("num_dups",num_dups)
        if num_dups:
            flash={
                "type": "error",
                "message": "%d duplicate jobs found"%num_dups,
            }
        else:
            flash={
                "type": "success",
                "message": "No duplicate jobs found",
            }
        return {
            "next": {
                "name": "job",
            },
            "flash": flash,
        }

    def get_percent_done(self,ids,context={}):
        vals={}
        for obj in self.browse(ids):
            if obj.tasks:
                n=0
                total=0
                for task in obj.tasks:
                    total+=task.est_hours or 0
                    if task.state=="done":
                        n+=task.est_hours or 0
                vals[obj.id]=round(n*100/total) if total else 0
            elif obj.time_entries:
                h=0
                for time in obj.time_entries:
                    h+=time.bill_hours or 0
                vals[obj.id]=round(h*100/obj.est_hours) if obj.est_hours else 0
            else:
                vals[obj.id]=0
        return vals

    def search_involved_user(self,clause,context={}):
        user_id=clause[2]
        return ["or",["users.id","=",user_id],["user_id","=",user_id]]

    def get_uninvoiced_amount(self,ids,context={}):
        vals={}
        for obj in self.browse(ids):
            if obj.bill_type=="hour":
                amt=0
                for t in obj.time_entries:
                    if t.state in ("draft","submitted","approved"):
                        amt+=t.amount or 0
            else:
                amt=None
            vals[obj.id]=amt
        return vals

    def get_uninvoiced_hours(self,ids,context={}):
        vals={}
        for obj in self.browse(ids):
            if obj.bill_type=="hour":
                h=0
                for t in obj.time_entries:
                    if t.state in ("draft","submitted","approved"):
                        h+=t.bill_hours or 0
            else:
                h=None
            vals[obj.id]=h
        return vals

    def get_approved_amount(self,ids,context={}):
        vals={}
        for obj in self.browse(ids):
            if obj.bill_type=="hour":
                amt=0
                for t in obj.time_entries:
                    if t.state=="approved":
                        amt+=t.amount or 0
            else:
                amt=None
            vals[obj.id]=amt
        return vals

    def get_approved_hours(self,ids,context={}):
        vals={}
        for obj in self.browse(ids):
            if obj.bill_type=="hour":
                h=0
                for t in obj.time_entries:
                    if t.state=="approved":
                        h+=t.bill_hours or 0
            else:
                h=None
            vals[obj.id]=h
        return vals

    def get_time_total(self,ids,context={}):
        vals={}
        for obj in self.browse(ids):
            hours=0
            amt=0
            for time in obj.time_entries:
                hours+=time.bill_hours or 0
                amt+=time.amount or 0
            vals[obj.id]={
                "total_bill_hours": hours,
                "total_bill_amount": amt,
            }
        return vals

    def get_time_users(self,ids,context={}):
        vals={}
        for obj in self.browse(ids):
            user_ids=[]
            for t in obj.time_entries:
                if not t.user_id.code:
                    continue
                user_ids.append(t.user_id.id)
            user_ids=list(set(user_ids))
            vals[obj.id]=user_ids
        return vals

    def get_time_users_preview(self,ids,context={}):
        vals={}
        for obj in self.browse(ids):
            user_ids=[]
            for t in obj.time_entries_other:
                if not t.user_id.code:
                    continue
                user_ids.append(t.user_id.id)
            user_ids=list(set(user_ids))
            vals[obj.id]=user_ids
        return vals

    def migrate(self,context={}):
        bg_job_id=context.get("job_id")
        cond=[]
        fields=["number","contact_id","name","start_date","due_date","state"]
        data=rpc_exec("job","search_read",[cond,fields])
        for i,r in enumerate(data):
            if bg_job_id:
                if tasks.is_aborted(bg_job_id):
                    return
                tasks.set_progress(bg_job_id,i*100/len(data),"Migrating job %s of %s."%(i+1,len(data)))
            print("-"*80)
            print(r)
            contact_name=r["contact_id"][1]
            vals={
                "name": contact_name,
            }
            res=get_model("contact").search([["name","=",contact_name]])
            if res:
                contact_id=res[0]
            else:
                contact_id=get_model("contact").create(vals)
            vals={
                "number": r["number"],
                "contact_id": contact_id,
                "name": r["name"],
                "start_date": r["start_date"],
                "due_date": r["due_date"],
                "state": r["state"],
            }
            res=self.search([["number","=",r["number"]]])
            if res:
                job_id=res[0]
                self.write([job_id],vals)
            else:
                job_id=self.create(vals)

    def migrate_prod(self,context={}):
        for obj in self.search_browse([]):
            #if obj.product_id:
            #    continue
            if not obj.service_id:
                continue
            if not obj.service_id.product_id:
                continue
            obj.write({"product_id":obj.service_id.product_id.id})

    def create_folder(self,ids,context={}):
        obj=self.browse(ids[0])
        if obj.folder_id:
            return
        contact=obj.contact_id
        parent_id=contact.create_folder()
        vals={
            "name": obj.number,
            "contact_id": obj.contact_id.id,
            "related_id": "jc.job,%s"%obj.id,
            "parent_id": parent_id,
        }
        folder_id=get_model("folder").create(vals)
        obj.write({"folder_id":folder_id})
        return folder_id

    def copy(self, ids, context):
        obj = self.browse(ids)[0]
        num=self._get_number(context=context)
        vals={
            "number": num,
            "state": "in_progress",
        }
        new_id = obj._copy(vals)[0]
        new_obj = self.browse(new_id)
        return {
            "next": {
                "name": "jc_job",
                "mode": "form",
                "active_id": new_id,
            },
            "flash": "Job %s copied to %s" % (obj.number, new_obj.number),
        }
        
Job.register()
