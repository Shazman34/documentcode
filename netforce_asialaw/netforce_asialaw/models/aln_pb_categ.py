from netforce.model import Model,fields,get_model
import time

class Categ(Model):
    _name="aln.pb.categ"
    _string="Probono Category"
    _audit_log=True
    _fields={
        "name": fields.Char("Name"),
    }
    _order="name"

Categ.register()
