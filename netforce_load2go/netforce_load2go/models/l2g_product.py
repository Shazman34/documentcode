from netforce.model import Model,fields,get_model
import time

class Product(Model):
    _name="l2g.product"
    _string="Product"
    _key=["name"]
    _fields={
        "name": fields.Char("Product Name",required=True),
        "width": fields.Decimal("Width (mm)"),
        "height": fields.Decimal("Height (mm)"),
        "length": fields.Decimal("Length (mm)"),
        "thickness": fields.Decimal("Thickness (mm)"),
        "weight": fields.Decimal("Weight (ton)",scale=3),
        "options": fields.One2Many("l2g.product.option","product_id","Product Options"),
        "num_options": fields.Integer("# Options",function="get_num_options"),
    }
    _order="name"

    def get_num_options(self,ids,context={}):
        vals={}
        for obj in self.browse(ids):
            vals[obj.id]=len(obj.options)
        return vals

Product.register()
