from netforce.model import Model,fields,get_model
from datetime import *
import time

class Assign(Model):
    _name="ht.assign"
    _string="Assignments"
    _name_field="number"
    _fields={
        "accom_type_id": fields.Many2One("ht.accom.type","Accomodation Type",required=True,search=True),
        "accom_id": fields.Many2One("ht.accom","Accomodation",required=True,search=True),
        "booking_id": fields.Many2One("ht.booking","Reservation",required=True,search=True,on_delete="cascade"),
        "from_date": fields.Date("From Date",required=True,search=True),
        "to_date": fields.Date("To Date",required=True,search=True),
        "num_nights": fields.Integer("Nights",function="get_num_nights"),
        "num_guests": fields.Integer("Num Guests"),
        "amount": fields.Decimal("Amount"),
    }

    def default_get(self, *args, context={}, **kw):
        vals=super().default_get(*args,context=context,**kw)
        res=vals.get("booking_id")
        if res:
            booking_id=res[0]
            booking=get_model("ht.booking").browse(booking_id)
            vals["from_date"]=booking.from_date
            vals["to_date"]=booking.to_date
            vals["num_guests"]=booking.num_guests
        return vals

    def get_num_nights(self, ids, context={}):
        vals={}
        for obj in self.browse(ids):
            if obj.from_date and obj.to_date:
                d0=datetime.strptime(obj.from_date,"%Y-%m-%d")
                d1=datetime.strptime(obj.to_date,"%Y-%m-%d")
                vals[obj.id]=(d1-d0).days
        return vals

    def update_amount(self,context={}):
        data=context["data"]
        accom_type_id=data["accom_type_id"]
        from_date=data["from_date"]
        to_date=data["to_date"]
        num_guests=data["num_guests"]
        amount=get_model("ht.rate").get_amount(accom_type_id,from_date,to_date,num_guests)
        data["amount"]=amount
        d0=datetime.strptime(from_date,"%Y-%m-%d")
        d1=datetime.strptime(to_date,"%Y-%m-%d")
        num_nights=(d1-d0).days
        data["num_nights"]=num_nights
        return data

Assign.register()
