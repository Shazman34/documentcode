from netforce.model import Model,fields,get_model

class OrderLine(Model):
    _name="nd.order.line"
    _string="Delivery Order Line"
    _fields={
        "order_id": fields.Many2One("nd.order","Delivery Order",required=True,on_delete="cascade"),
        "product_id": fields.Many2One("product","Product",required=True,search=True),
        "image": fields.File("Image",function="_get_related",function_context={"path":"product_id.image"}),
        "qty": fields.Decimal("Qty",required=True),
    }

OrderLine.register()
