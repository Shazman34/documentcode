from netforce.model import Model,fields,get_model
import time

class Option(Model):
    _name="l2g.product.option"
    _string="Option"
    _fields={
        "name": fields.Char("Option Name",required=True),
        "sequence": fields.Integer("Sequence"),
        "product_id": fields.Many2One("l2g.product","Product",required=True),
        "weight": fields.Decimal("Weight (ton)",scale=3),
    }
    _order="sequence,id"

Option.register()
