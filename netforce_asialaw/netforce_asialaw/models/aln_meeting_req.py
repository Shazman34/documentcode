from netforce.model import Model,fields,get_model
import time

class MeetingReq(Model):
    _name="aln.meeting.req"
    _string="Meeting Request"
    _fields={
        "date": fields.Date("Date",required=True),
        "client_id": fields.Many2One("aln.client","Client",required=True),
        "job_id": fields.Many2One("aln.job","Job",required=True),
    }
    _defaults={
        "date": lambda *a: time.strftime("%Y-%m-%d"),
    }

MeetingReq.register()
