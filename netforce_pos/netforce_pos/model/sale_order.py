from netforce.model import Model,fields,get_model
from netforce import access

class SaleOrder(Model):
    _inherit="sale.order"

    def pos_restore(self,ids,context={}):
        access.set_active_user(1)
        obj=self.browse(ids)[0]
        if obj.state!="draft":
            raise Exception("Invalid order status")
        res=obj.copy_to_cart()
        cart_id=res["cart_id"]
        obj.delete()
        return {
            "cart_id": cart_id,
        }

SaleOrder.register()
