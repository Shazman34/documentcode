from netforce.model import Model,fields,get_model
import time

class ProductType(Model):
    _name="l2g.product.type"
    _string="Product Type"
    _key=["name"]
    _fields={
        "name": fields.Char("Product Type Name",required=True),
    }
    _order="name"

ProductType.register()
