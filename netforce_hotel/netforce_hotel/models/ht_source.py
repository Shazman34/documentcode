from netforce.model import Model,fields,get_model
import time

class Source(Model):
    _name="ht.source"
    _string="Reservation Source"
    _fields={
        "name": fields.Char("Name",required=True,search=True),
        "is_ota": fields.Boolean("Is OTA"),
    }

Source.register()
