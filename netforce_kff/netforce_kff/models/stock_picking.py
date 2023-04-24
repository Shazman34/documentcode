from netforce.model import Model,fields,get_model
from netforce import access
from datetime import *
from decimal import *

class Picking(Model):
    _inherit="stock.picking"

Picking.register()
