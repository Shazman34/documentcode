from netforce.model import Model,fields,get_model
import time

class Prod(Model):
    _name="l2g.booking.product"
    _fields={
        "booking_id": fields.Many2One("l2g.booking","Booking"),
        "product_id": fields.Many2One("l2g.product","Product",required=True),
        "qty": fields.Decimal("Qty",required=True),
        "weight": fields.Decimal("Weight",function="get_weight"),
        "width": fields.Decimal("Width (mm)",function="_get_related",function_context={"path":"product_id.width"}),
        "height": fields.Decimal("Height (mm)",function="_get_related",function_context={"path":"product_id.height"}),
        "length": fields.Decimal("Length (mm)",function="_get_related",function_context={"path":"product_id.length"}),
        "thickness": fields.Decimal("Thicknes (mm)",function="_get_related",function_context={"path":"product_id.thickness"}),
    }
    _defaults={
        "qty": 1,
    }
    _order="id"

    def get_weight(self,ids,context={}):
        vals={}
        for obj in self.browse(ids):
            prod=obj.product_id
            vals[obj.id]=(prod.weight or 0)*obj.qty
        return vals

Prod.register()
