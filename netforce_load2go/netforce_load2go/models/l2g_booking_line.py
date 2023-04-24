from netforce.model import Model,fields,get_model
from netforce import access
import googlemaps
from decimal import *
from datetime import *
import time
import json

API_KEY="AIzaSyAKs3alHGFG4ckYe6b0G67DbViVJX3rgV0"

class BookingLine(Model):
    _name="l2g.booking.line"
    _name_field="number"
    _audit_log=True
    _fields={
        "booking_id": fields.Many2One("l2g.booking","Booking",required=True,on_delete="cascade",search=True),
        "truck_type_id": fields.Many2One("l2g.truck.type","Truck Type",required=True,search=True),
        "weight_range_id": fields.Many2One("l2g.weight.range","Weight Range",required=True,search=True),
        "price": fields.Decimal("Client Price"),
        "amount": fields.Decimal("Client Amount",function="get_amount"),
        "driver_price": fields.Decimal("Driver Price"),
        "driver_id": fields.Many2One("l2g.driver","Driver"),
        "truck_id": fields.Many2One("l2g.truck","Truck"),
        "qty": fields.Integer("Qty"),
        "price_id": fields.Many2One("l2g.price","Price Rate"),
        "customer_cancel_fee": fields.Decimal("Customer Cancel Fee"),
        "driver_cancel_fee": fields.Decimal("Driver Cancel Fee"),
    }
    _order="id desc"
    _defaults={
        "qty": 1,
    }

    def get_amount(self,ids,context={}):
        vals={}
        for obj in self.browse(ids):
            vals[obj.id]=(obj.price or 0)*(obj.qty or 0)
        return vals

    def inc_qty(self,ids,context={}):
        obj=self.browse(ids[0])
        obj.write({"qty":obj.qty+1})

    def dec_qty(self,ids,context={}):
        obj=self.browse(ids[0])
        if obj.qty>=2:
            obj.write({"qty":obj.qty-1})
        else:
            obj.delete()

BookingLine.register()
