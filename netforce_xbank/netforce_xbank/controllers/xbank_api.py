from netforce.controller import Controller
from netforce.model import Model, fields, get_model
from netforce import database
from netforce import access
from netforce.logger import audit_log
import json
from netforce import utils
from decimal import *

class API(Controller):
    _path = "/api"

    def post(self):
        print("#"*80)
        print("API request")
        print("#"*80)
        req = json.loads(self.request.body.decode())
        print("req",req)
        method=req["method"]
        if method=="new_deposit":
            user=req["user"]
            payment_currency=req["payment_currency"]
            amount=req["amount"]
            amount_currency=req["amount_currency"]
            with database.Transaction():
                access.set_active_user(1)
                res=get_model("xb.account").search([["name","=",user]])
                if not res:
                    raise Exception("Invalid user: %s"%user)
                acc_id=res[0]
                acc=get_model("xb.account").browse(acc_id)
                addr_id=acc.new_addr_xbt()
                addr=get_model("xb.address").browse(addr_id)
                res=get_model("xb.price").search([["product","=","btc_thb"],["source","=","xbank"]],order="time desc",limit=1)
                if not res:
                    raise Exception("Price not found")
                price_id=res[0]
                price=get_model("xb.price").browse(price_id)
                pay_amount=(Decimal(amount)/price.ask).quantize(Decimal("0.00000001"))
                res={
                    "payment_url": "bitcoin:%s?amount=%s"%(addr.address,pay_amount),
                    "payment_address": addr.address,
                    "payment_amount": pay_amount,
                    "payment_qr_code": "https://chart.googleapis.com/chart?chs=250x250&cht=qr&chl=bitcoin:%s&amount=%s"%(addr.address,pay_amount),
                }
        elif method=="check_balance":
            address=req["address"]
            with database.Transaction():
                access.set_active_user(1)
                res=get_model("xb.address").search([["address","=",address]])
                if not res:
                    raise Exception("Invalid user: %s"%user)
                addr_id=res[0]
                addr=get_model("xb.address").browse(addr_id)
                res={
                    "balance0": str(addr.balance0),
                    "balance1": str(addr.balance1),
                    "balance2": str(addr.balance2),
                    "balance3": str(addr.balance3),
                    "balance10": str(addr.balance10),
                }
        else:
            raise Exception("Invalid method")
        self.add_header("Access-Control-Allow-Origin","*")
        self.write(utils.json_dumps(res))

API.register()
