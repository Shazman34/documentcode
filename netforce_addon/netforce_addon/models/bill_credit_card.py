from netforce.model import Model,fields
import time

class CreditCard(Model):
    _name="bill.credit.card"
    _fields={
        "brand": fields.Char("Brand",required=True),
        "country": fields.Char("Country"),
        "exp_month": fields.Integer("Exp. Month",required=True),
        "exp_year": fields.Integer("Exp. Year",required=True),
        "last4": fields.Char("Last 4 Digits",required=True),
        "date_added": fields.Date("Date Addded",required=True),
    }
    _defaults={
        "date_added": lambda *a: time.strftime("%Y-%m-%d"),
    }

CreditCard.register()
