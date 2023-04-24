from netforce.model import Model,fields,get_model
import requests
import json
from decimal import *
from pprint import pprint

class Task(Model):
    _name="nd.task"
    _string="Task"
    _name_field="title"
    _fields={
        "job_id": fields.Many2One("nd.job","Job",required=True,search=True,on_delete="cascade"),
        "sequence": fields.Integer("Sequence"),
        "title": fields.Char("Title"),
        "details": fields.Text("Details"),
        "est_duration": fields.Decimal("Est. Duration (Minutes)"),
        "est_start_time": fields.Char("Est. Start Time"),
        "est_end_time": fields.Char("Est. End Time"),
        "act_start_time": fields.Char("Act. Start Time"),
        "act_end_time": fields.Char("Act. End Time"),
        "type": fields.Selection([["pickup","Pickup"],["delivery","Delivery"],["return","Return"],["other","Other"]],"Type",required=True,search=True),
        "state": fields.Selection([["waiting","Waiting"],["in_progress","In Progress"],["done","Completed"],["error","Can not complete task"]],"Status",required=True,search=True),
        "route_id": fields.Many2One("nd.route","Delivery Route",search=True),
        "order_id": fields.Many2One("nd.order","Delivery Order",search=True),
        "require_gps": fields.Boolean("Require GPS"),
        "title_func": fields.Char("Title",function="get_title"),
    }
    _order="job_id,sequence"
    _defaults={
        "state": "planned",
    }

    def set_in_progress(self,ids,context={}):
        obj=self.browse(ids[0])
        if obj.job_id.state!="in_progress":
            obj.job_id.set_in_progress()
        obj.write({"state":"in_progress"},context=context)
        if obj.route_id:
            obj.route_id.set_in_progress(context=context)

    def set_done(self,ids,context={}):
        obj=self.browse(ids[0])
        if obj.job_id.state!="in_progress":
            raise Exception("Task status can only be changed while job is in progress")
        obj.write({"state":"done"},context=context)
        if obj.route_id:
            obj.route_id.set_done(context=context)

    def set_error(self,ids,context={}):
        obj=self.browse(ids[0])
        if obj.job_id.state!="in_progress":
            raise Exception("Task status can only be changed while job is in progress")
        obj.write({"state":"error"},context=context)
        if obj.route_id:
            obj.route_id.set_error(context=context)

    def set_waiting(self,ids,context={}):
        obj=self.browse(ids[0])
        if obj.job_id.state!="in_progress":
            raise Exception("Task status can only be changed while job is in progress")
        obj.write({"state":"waiting"},context=context)
        if obj.route_id:
            obj.route_id.set_waiting(context=context)

    def pickup_done(self,ids,context={}):
        print("pickup_done",ids,context)
        obj=self.browse(ids[0])
        obj.write({"state":"done"},context=context)
        if not obj.route_id:
            raise Exception("Missing route in task")
        obj.route_id.set_in_progress(context=context)

    def delivery_done(self,ids,context={}):
        print("delivery_done",ids,context)
        obj=self.browse(ids[0])
        obj.write({"state":"done"},context=context)
        if not obj.order_id:
            raise Exception("Missing order in task")
        obj.order_id.set_done(context=context)

    def delivery_done_undo(self,ids,context={}):
        print("delivery_done_undo",ids,context)
        obj=self.browse(ids[0])
        obj.write({"state":"waiting"},context=context)
        if not obj.order_id:
            raise Exception("Missing order in task")
        obj.order_id.set_waiting(context=context)

    def return_done(self,ids,context={}):
        print("return_done",ids,context)
        obj=self.browse(ids[0])
        obj.write({"state":"done"},context=context)
        if not obj.route_id:
            raise Exception("Missing route in task")
        obj.route_id.set_done(context=context)

    def get_title(self,ids,context={}):
        vals={}
        for obj in self.browse(ids):
            if obj.type=="pickup":
                title="Pickup products (%s)"%(obj.route_id.round_id.period_id.name if obj.route_id else "N/A")
            elif obj.type=="delivery":
                title="Deliver to %s"%(obj.order_id.customer_id.first_name if obj.order_id else "N/A")
            elif obj.type=="return":
                title="Return from route (%s)"%(obj.route_id.round_id.period_id.name if obj.route_id else "N/A")
            else:
                title="N/A"
            vals[obj.id]=title
        return vals

Task.register()
