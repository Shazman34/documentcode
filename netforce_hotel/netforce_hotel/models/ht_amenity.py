from netforce.model import Model,fields,get_model
import time

class Amenity(Model):
    _name="ht.amenity"
    _string="Amenity"
    _fields={
        "name": fields.Char("Name",required=True,search=True),
    }
    _order="name"

Amenity.register()
