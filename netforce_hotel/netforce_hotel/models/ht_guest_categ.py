from netforce.model import Model,fields,get_model
import time

class Categ(Model):
    _name="ht.guest.categ"
    _string="Guest Category"
    _fields={
        "name": fields.Char("Name",required=True,search=True),
    }

Categ.register()
