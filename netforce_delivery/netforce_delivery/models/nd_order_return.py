from netforce.model import Model,fields,get_model

class OrderReturn(Model):
    _name="nd.order.return"
    _fields={
        "order_id": fields.Many2One("nd.order","Delivery Order",required=True,on_delete="cascade"),
        "product_id": fields.Many2One("product","Product",required=True),
        "image": fields.File("Image",function="_get_related",function_context={"path":"product_id.image"}),
        "qty": fields.Decimal("Return Qty",required=True),
    }

OrderReturn.register()
