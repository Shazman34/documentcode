from netforce.model import Model,fields,get_model
import time

class Industry(Model):
    _name="aln.industry"
    _string="Industry"
    _audit_log=True
    _fields={
        "name": fields.Char("Name"),
    }
    _order="name"

Industry.register()
