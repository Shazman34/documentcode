from netforce.controller import Controller
from netforce.model import Model, fields, get_model
from netforce import database
from netforce import access
from netforce.logger import audit_log
import json

class UpdateSupOrder(Controller):
    _path = "/gt_update_sup_order"

    def post(self):
        print("#"*80)
        print("gt_update_sup_order")
        try:
            req=json.loads(self.request.body.decode("utf-8"))
            print("req",req)
            open("/tmp/gt_update_sup_order.log","a").write(json.dumps(req)+"\n")
            order_id=req["order_id"]
            state=req["state"]
            fill_price=req.get("fill_price")
            with database.Transaction():
                access.set_active_user(1)
                res=get_model("gt.sup.order").search([["number","=",order_id]])
                if not res:
                    raise Exception("Order not found: '%s'"%order_id)
                order_id=res[0]
                order=get_model("gt.sup.order").browse(order_id)
                if order.state!="filled": # TODO: fix connector out of order messages
                    order.write({"state":state})
                if fill_price:
                    order.write({"fill_price":fill_price})
        except Exception as e:
            import traceback
            traceback.print_exc()
            with database.Transaction():
                audit_log("Failed to update order",details=str(e))

UpdateSupOrder.register()
