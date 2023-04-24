from netforce.controller import Controller
from netforce.model import Model, fields, get_model
from netforce import database
from netforce import access
from decimal import *
import time

class PaypalNotif(Controller):
    _path = "/payment_paypal_notif"

    # XXX: add server checking
    def post(self):
        post_data=self.get_argument("PMGWRESP2")
        token=post_data[32:32+12]
        with database.Transaction():
            access.set_active_user(1)
            res=get_model("payment.transaction").search([["paypal_token","=",token]])
            if not res:
                raise Exception("Payment transaction not found: paypal_token=%s"%token)
            trans_id=res[0]
            trans=get_model("payment.transaction").browse(trans_id)
            if trans.state=="error":
                raise Exception("Transaction failed already (trans_id=%s)"%trans.id)
            elif trans.state=="done":
                return
            try:
                resp_code=post_data[97:97+2]
                if resp_code!="00":
                    raise Exception("Wrong response code: %s"%resp_code)
                amount=Decimal(post_data[85:85+12])/100
                if amount!=trans.amount:
                    raise Exception("Wrong amount: %s"%amount)
                cur_no=post_data[29:29+3]
                res=get_model("currency").search([["iso_number","=",cur_no]])
                if not res:
                    raise Exception("Currency not found: %s"%cur_no)
                currency_id=res[0]
                if currency_id!=trans.currency_id.id:
                    raise Exception("Wrong currency: %s"%cur_no)
                trans.payment_received()
            except Exception:
                import traceback
                error=traceback.format_exc()
                open("/tmp/payment_error.log","a").write("[%s] %s\n"%(time.strftime("%Y-%m-%d %H:%M:%S"),error))
                trans.payment_error(context={"error": error})

PaypalNotif.register()
