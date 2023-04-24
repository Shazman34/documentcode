from netforce.model import Model, fields, get_model
import time

class JobStatus(Model):
    _name="jc.job.status"
    _string="Job Status Details"
    _fields={
        "job_id": fields.Many2One("jc.job","Job",required=True,on_delete="cascade"),
        "date": fields.Date("Date",required=True),
        "description": fields.Text("Status Details",required=True),
    }
    _order="date desc,id desc"
    _defaults={
        "date": lambda *a: time.strftime("%Y-%m-%d"),
    }

JobStatus.register()
