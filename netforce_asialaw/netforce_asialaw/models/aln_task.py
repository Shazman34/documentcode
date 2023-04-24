from netforce.model import Model,fields,get_model
from netforce import access
import time

class Task(Model):
    _name="aln.task"
    _string="Task"
    _name_field="title"
    _audit_log=True
    _fields={
        "job_id": fields.Many2One("aln.job","Job",required=True,search=True),
        "date": fields.Date("Task Date",required=True,search=True),
        "title": fields.Char("Task Title",search=True,required=True),
        "meetings": fields.One2Many("aln.meeting","task_id","Meetings"),
        "documents": fields.One2Many("aln.doc","task_id","Documents"),
        "bill_reqs": fields.One2Many("aln.bill.req","task_id","Billing Requests"),
        "messages": fields.One2Many("aln.message","task_id","Messages"),
        "logs": fields.One2Many("log","related_id","Audit Log"),
        "access": fields.Selection([["all","View by all"],["team","View by team only"],["client_team","View by client and team"]],"Access"),
    }
    _order="date desc,id desc"
    _defaults={
        "date": lambda *a: time.strftime("%Y-%m-%d"),
    }

Task.register()
