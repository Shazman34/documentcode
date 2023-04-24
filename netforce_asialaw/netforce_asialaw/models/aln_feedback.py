from netforce.model import Model,fields,get_model
import time

class Feedback(Model):
    _name="aln.feedback"
    _string="Feedback"
    _audit_log=True
    _fields={
        "date": fields.Date("Date",required=True,search=True),
        "client_id": fields.Many2One("aln.client","Client",required=True,search=True),
        "job_id": fields.Many2One("aln.job","Case",search=True),
        "lawyer_id": fields.Many2One("aln.lawyer","Lawyer",search=True),
        "rating": fields.Selection([["1","1"],["2","2"],["3","3"],["4","4"],["5","5"]],"Rating"),
        "remarks": fields.Text("Remarks"),
    }
    _order="date desc,id desc"
    _defaults={
        "date": lambda *a: time.strftime("%Y-%m-%d"),
    }

Feedback.register()
