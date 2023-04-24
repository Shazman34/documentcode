from netforce.controller import Controller
from netforce.model import get_model
from netforce import database
from netforce import access
from decimal import *
import requests
import urllib
import time
import paypalrestsdk

class PaypalReturn(Controller):
    _path = "/payment_paypal_return"

    def get(self):
        dbname=self.get_argument("dbname")
        database.set_active_db(dbname)
        payment_id=self.get_argument("paymentId")
        token=self.get_argument("token")
        payer_id=self.get_argument("PayerID")
        with database.Transaction():
            access.set_active_user(1)
            res=get_model("payment.transaction").search([["paypal_token","=",payment_id]])
            if not res:
                raise Exception("Payment transaction not found: paypal_id=%s"%payment_id)
            trans_id=res[0]
            trans=get_model("payment.transaction").browse(trans_id)
            if trans.state=="error":
                raise Exception("Transaction failed already (trans_id=%s)"%trans.id)
            elif trans.state=="done":
                if trans.return_url:
                    url=trans.return_url.replace("{transaction_id}",str(trans.id))
                    self.redirect(url)
                return
            try:
                meth=trans.pay_method_id
                if not meth.paypal_client_id:
                    raise Exception("Missing Paypal Client ID")
                if not meth.paypal_secret:
                    raise Exception("Missing Paypal Secret")
                api=paypalrestsdk.Api({
                    "mode": meth.paypal_sandbox and "sandbox" or "live",
                    "client_id": meth.paypal_client_id,
                    "client_secret": meth.paypal_secret,
                })
                pmt=paypalrestsdk.Payment.find(payment_id,api=api)
                res=pmt.execute({"payer_id":payer_id})
                if not res:
                    raise Exception(pmt.error)
                #trans.write({"paypal_trans_no": trans_no}) # XXX: check how to get this with rest api
                trans.payment_received()
                if trans.return_url:
                    url=trans.return_url.replace("{transaction_id}",str(trans.id))
                    self.redirect(url)
            except Exception:
                import traceback
                error=traceback.format_exc()
                open("/tmp/payment_error.log","a").write("[%s] %s\n"%(time.strftime("%Y-%m-%d %H:%M:%S"),error))
                trans.payment_error(context={"error":error})
                if trans.error_url:
                    url=trans.error_url.replace("{transaction_id}",str(trans.id))
                    self.redirect(url)

PaypalReturn.register()
