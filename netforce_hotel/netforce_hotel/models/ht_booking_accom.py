from netforce.model import Model,fields,get_model
import time

class BookingAccom(Model):
    _name="ht.booking.accom"
    _fields={
        "booking_id": fields.Many2One("ht.booking","Booking",required=True,on_delete="cascade"),
        "accom_type_id": fields.Many2One("ht.accom.type","Type",required=True),
        "accom_id": fields.Many2One("ht.accom","Assignment",required=True),
    }

BookingAccom.register()
