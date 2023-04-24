from netforce.model import Model,fields,get_model
import time

class Fee(Model):
    _name="ed.fee"
    _string="Fee"
    _name_field="title"
    _fields={
        "student_id": fields.Many2One("ed.student","Student",required=True),
        "due_date": fields.Date("Due Date",required=True,search=True),
        "title": fields.Char("Title",required=True,search=True),
        "description": fields.Text("Description",search=True),
        "amount": fields.Decimal("Fee Amount",required=True),
        "amount_paid": fields.Decimal("Paid Amount",function="get_amount",function_multi=True),
        "amount_due": fields.Decimal("Due Amount",function="get_amount",function_multi=True),
        "payments": fields.One2Many("ed.payment","fee_id","Payments"),
    }
    _defaults={
        "date": lambda *a: time.strftime("%Y-%m-%d"),
    }

    def get_amount(self,ids,context={}):
        vals={}
        for obj in self.browse(ids):
            paid=0
            for pmt in obj.payments:
                paid+=pmt.amount or 0
            vals[obj.id]={
                "amount_paid": paid,
                "amount_due": (obj.amount or 0)-paid,
            }
        return vals

Fee.register()
