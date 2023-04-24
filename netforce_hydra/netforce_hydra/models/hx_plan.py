from netforce.model import Model,fields,get_model
from netforce import database
from netforce import utils
import time
import random

class Plan(Model):
    _name="hx.plan"
    _string="Price Plan"
    _fields={
        "name": fields.Char("Name",required=True),
        "sequence": fields.Integer("Sequence"),
        "addons": fields.Many2Many("hx.addon","Addons"),
    }
    _order="sequence,name"

Plan.register()
