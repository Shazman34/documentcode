from netforce.model import Model,fields,get_model
from netforce import access
from netforce import database
from netforce import utils

class PriceParamGroup(Model):
    _name="gt.price.param.group"
    _string="Price Parameter Group"
    _fields={
        "sequence": fields.Integer("Sequence"),
        "name": fields.Char("Name",required=True),
        "description": fields.Text("Description"),
        "color": fields.Char("Color"),
    }
    _order="sequence,name"

PriceParamGroup.register()
