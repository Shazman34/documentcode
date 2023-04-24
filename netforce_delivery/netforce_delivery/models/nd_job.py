from netforce.model import Model,fields,get_model
from netforce import access
from datetime import *
import time
import requests
from pprint import pprint
import math
import json
from .polyline import polyline_decode
import random

class Job(Model):
    _name="nd.job"
    _string="Job"
    _audit_log=True
    _name_field="number"
    _fields={
        "number": fields.Char("Number",required=True,search=True),
        "driver_id": fields.Many2One("nd.driver","Driver",required=True,search=True),
        "date": fields.Date("Job Date",required=True,search=True),
        "state": fields.Selection([["draft","Draft"],["waiting","Waiting"],["in_progress","In Progress"],["done","Completed"],["error","Can not complete job"]],"Status",required=True,search=True),
        "tasks": fields.One2Many("nd.task","job_id","Tasks"),
        "num_tasks": fields.Integer("Num Tasks",function="get_num_tasks"),
        "num_tasks_done": fields.Integer("Tasks Completed",function="get_num_tasks_done"),
        "amount": fields.Decimal("Pay Amount"),
        "today": fields.Boolean("Today",store=False,function_search="search_today"),
        "today_p1": fields.Boolean("Today+1",store=False,function_search="search_today_p1"),
        "today_p2": fields.Boolean("Today+2",store=False,function_search="search_today_p2"),
        "comments": fields.Text("Comments"),
        "title": fields.Char("Title",required=True),
        "bonus_amount": fields.Decimal("Bonus Amount"),
        "bonus_min_deliveries": fields.Decimal("Bonus Minimum Deliveries"),
        "bonus_min_on_time_percent": fields.Decimal("Bonus Minimum On-Time %"),
        "amount_due": fields.Decimal("Amount Due",function="get_amount_due"),
    }
    _order="date,id"

    def _get_number(self,context={}):
        n="%05d"%random.randint(0,99999)
        return "J%s"%n

    _defaults={
        "state": "draft",
        "date": lambda *a: time.strftime("%Y-%m-%d"),
        "number": _get_number,
    }

    def name_get(self,ids,context={}):
        res=[]
        for obj in self.browse(ids):
            name="%s-%s"%(obj.driver_id.name,obj.date[5:])
            res.append([obj.id,name])
        return res

    def name_search(self,name,condition,*args,**kw):
        ids=self.search(condition)
        return self.name_get(ids)

    def search_today(self,clause,context={}):
        d=datetime.today().strftime("%Y-%m-%d")
        ids=self.search([["date","=",d]])
        return ["id","in",ids]

    def search_today_p1(self,clause,context={}):
        d=(datetime.today()+timedelta(days=1)).strftime("%Y-%m-%d")
        ids=self.search([["date","=",d]])
        return ["id","in",ids]

    def search_today_p2(self,clause,context={}):
        d=(datetime.today()+timedelta(days=2)).strftime("%Y-%m-%d")
        ids=self.search([["date","=",d]])
        return ["id","in",ids]

    def get_num_tasks(self,ids,context={}):
        vals={}
        for obj in self.browse(ids):
            vals[obj.id]=len(obj.tasks)
        return vals

    def set_in_progress(self,ids,context={}):
        obj=self.browse(ids[0])
        obj.write({"state":"in_progress"},context=context)

    def set_done(self,ids,context={}):
        obj=self.browse(ids[0])
        obj.write({"state":"done"},context=context)

    def set_waiting(self,ids,context={}):
        obj=self.browse(ids[0])
        obj.write({"state":"waiting"},context=context)

    def set_error(self,ids,context={}):
        obj=self.browse(ids[0])
        obj.write({"state":"error"},context=context)

    def start_job(self,ids,context={}):
        obj=self.browse(ids[0])
        obj.write({"state":"in_progress"},context=context)

    def stop_job(self,ids,context={}):
        obj=self.browse(ids[0])
        obj.write({"state":"waiting"},context=context)

    def get_num_tasks_done(self,ids,context={}):
        vals={}
        for obj in self.browse(ids):
            n=0
            for t in obj.tasks:
                if t.state=="done":
                    n+=1
            vals[obj.id]=n
        return vals

    def get_amount_due(self,ids,context={}):
        vals={}
        for obj in self.browse(ids):
            amt=obj.amount or 0
            amt+=obj.bonus_amount or 0
            vals[obj.id]=amt
        return vals

Job.register()
