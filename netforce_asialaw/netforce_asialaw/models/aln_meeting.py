from netforce.model import Model,fields,get_model
import time

class Meeting(Model):
    _name="aln.meeting"
    _string="Meeting"
    _name_field="subject"
    _audit_log=True
    _fields={
        "date": fields.Date("Date",required=True,search=True),
        "client_id": fields.Many2One("aln.client","Client",required=True,search=True),
        "job_id": fields.Many2One("aln.job","Job",search=True),
        "task_id": fields.Many2One("aln.task","Task",search=True),
        "subject": fields.Char("Subject",search=True),
        "logs": fields.One2Many("log","related_id","Audit Log"),
        "state": fields.Selection([["requested","Requested"],["confirmed","Confirmed"],["done","Completed"]],"Status",required=True,search=True),
    }
    _order="date desc,id desc"
    _defaults={
        "date": lambda *a: time.strftime("%Y-%m-%d"),
        "state": "requested",
    }

Meeting.register()
