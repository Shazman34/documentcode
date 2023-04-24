from netforce.model import Model,fields,get_model
import time

class Payment(Model):
    _name="aln.payment"
    _string="Payment"
    _fields={
        "date": fields.Date("Date",required=True),
        "client_id": fields.Many2One("aln.client","Client",required=True),
        "job_id": fields.Many2One("aln.job","Job",required=True),
        "amount": fields.Decimal("Payment Amount"),
    }
    _defaults={
        "date": lambda *a: time.strftime("%Y-%m-%d"),
    }

Payment.register()
