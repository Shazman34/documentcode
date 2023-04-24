from netforce.model import Model,fields,get_model
import time

class Area(Model):
    _name="aln.practice.area"
    _string="Practice Area"
    _audit_log=True
    _fields={
        "name": fields.Char("Name"),
    }
    _order="name"

Area.register()
