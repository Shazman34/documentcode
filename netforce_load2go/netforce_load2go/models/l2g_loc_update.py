from netforce.model import Model,fields,get_model
import time

class LocUpdate(Model):
    _name="l2g.loc.update"
    _string="Location Updates"
    _fields={
        "time": fields.DateTime("Time",required=True,index=True),
        "driver_id": fields.Many2One("l2g.driver","Driver"),
        "coords": fields.Char("Coords",required=True),
    }
    _defaults={
        "time": lambda *a: time.strftime("%Y-%m-%d %H:%M:%S"),
    }
    _order="time desc,id desc"

LocUpdate.register()
