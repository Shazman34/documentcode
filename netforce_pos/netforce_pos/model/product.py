from netforce.model import Model,fields,get_model
from netforce import access

class Product(Model):
    _inherit="product"

    def pos_add_to_cart(self,ids,context={}):
        access.set_active_user(1)
        obj=self.browse(ids[0])
        cart_id=context.get("cart_id")
        if not cart_id:
            vals={}
            cart_id=get_model("ecom2.cart").create(vals)
        res=get_model("ecom2.cart.line").search([["cart_id","=",cart_id],["product_id","=",obj.id]])
        if res:
            line_id=res[0]
            line=get_model("ecom2.cart.line").browse(line_id)
            line.write({"qty":line.qty+1})
        else:
            vals={
                "cart_id": cart_id,
                "product_id": obj.id,
                "qty": 1,
            }
            get_model("ecom2.cart.line").create(vals)
        return {
            "cookies": {
                "cart_id": cart_id,
            },
            "next": {
                "name": "pos_cart_m",
                "target": "sub_action",
            },
        }

Product.register()
