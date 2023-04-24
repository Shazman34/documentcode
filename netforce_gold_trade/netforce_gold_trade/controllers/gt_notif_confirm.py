from netforce.controller import Controller
from netforce.model import Model, fields, get_model
from netforce import database
from netforce import access
from netforce.logger import audit_log
import json

class Notif(Controller):
    _path = "/gt_notif_confirm"

    def get(self):
        dbname=self.request.headers.get("X-Database")
        self.write("dbname '%s'"%dbname)

    def post(self):
        print("#"*80)
        print("gt_notif_confirm")
        try:
            req=json.loads(self.request.body.decode("utf-8"))
            print("req",req)
            order_no=req["order_no"]
            match_price=req["match_price"]
            confirm_time=req["confirm_time"]
            with database.Transaction():
                access.set_active_user(1)
                audit_log("Received pending order confirmation",details=str(req))
                res=get_model("gt.cust.order").search([["number","=",order_no]])
                if not res:
                    raise Exception("Order not found: %s"%order_no)
                order_id=res[0]
                order=get_model("gt.cust.order").browse(order_id)
                order.confirm(context={"match_price":match_price,"confirm_time":confirm_time})
        except Exception as e:
            print("!"*80)
            print("GT NOTIF ERROR")
            import traceback
            traceback.print_exc()
            with database.Transaction():
                audit_log("Failed to process notification",details=str(e))

Notif.register()
