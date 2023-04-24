from netforce.model import Model,fields,get_model
from netforce import database
from datetime import *
import time

class Order(Model):
    _name="xb.order"
    _string="Customer Order"
    _name_field="number"
    _fields={
        "number": fields.Char("Number",required=True),
        "date_created": fields.DateTime("Date Created",required=True),
        "account_id": fields.Many2One("xb.account","Account",required=True),
        "product_id": fields.Many2One("product","Product",required=True),
        "unit_price": fields.Decimal("Unit Price",required=True),
        "qty": fields.Decimal("Qty",scale=6,required=True),
        "amount": fields.Decimal("Amount",function="get_amount"),
    }
    _defaults={
        "date_created": lambda *a: time.strftime("%Y-%m-%d %H:%M:%S"),
    }
    _order="date_created desc"

Order.register()
