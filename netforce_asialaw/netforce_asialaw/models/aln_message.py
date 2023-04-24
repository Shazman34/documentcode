from netforce.model import Model,fields,get_model
from netforce import access
import time

class Message(Model):
    _name="aln.message"
    _string="Message"
    _name_field="title"
    _audit_log=True
    _fields={
        "date": fields.Date("Task Date",required=True,search=True),
        "message": fields.Text("Message",search=True),
        "task_id": fields.Many2One("aln.task","Task",required=True,search=True),
        "client_id": fields.Many2One("aln.client","Client",required=True,search=True),
    }
    _defaults={
        "date": lambda *a: time.strftime("%Y-%m-%d"),
    }

Message.register()
