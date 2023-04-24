from netforce.model import Model,fields,get_model
import time

class Payment(Model):
    _name="ed.payment"
    _string="Payment"
    _fields={
        "date": fields.Date("Date",required=True,search=True),
        "student_id": fields.Many2One("ed.student","Student",required=True),
        "fee_id": fields.Many2One("ed.fee","Fee"),
        "amount": fields.Decimal("Paid Amount",required=True),
    }
    _defaults={
        "date": lambda *a: time.strftime("%Y-%m-%d"),
    }

Payment.register()
