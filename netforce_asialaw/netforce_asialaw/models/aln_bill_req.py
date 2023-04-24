from netforce.model import Model,fields,get_model
import time

class BillReq(Model):
    _name="aln.bill.req"
    _string="Billing Request"
    _fields={
        "date": fields.Date("Date",required=True),
        "client_id": fields.Many2One("aln.client","Client",required=True),
        "job_id": fields.Many2One("aln.job","Job",required=True),
        "task_id": fields.Many2One("aln.task","Task",search=True),
        "amount": fields.Decimal("Billing Amount"),
    }
    _order="date desc,id desc"
    _defaults={
        "date": lambda *a: time.strftime("%Y-%m-%d"),
    }

BillReq.register()
