from netforce.model import Model,fields,get_model
import time

class Location(Model):
    _name="l2g.location"
    _string="Location"
    _fields={
        "name": fields.Char("Location Name"),
        "region_id": fields.Many2One("l2g.province","Region"),
    }
    _order="name"

Location.register()
