from netforce.controller import Controller
from netforce.model import get_model
from netforce import database
from netforce import access

class PaypalCancel(Controller):
    _path = "/payment_paypal_cancel"

    def get(self):
        token=self.get_argument("token")
        with database.Transaction():
            access.set_active_user(1)
            res=get_model("payment.transaction").search([["paypal_token","=",token]])
            if not res:
                raise Exception("Payment transaction not found: paypal_token=%s"%token)
            trans_id=res[0]
            trans=get_model("payment.transaction").browse(trans_id)
            error="Payment canceled by user"
            trans.payment_error(context={"error": error})
            if trans.error_url:
                url=trans.error_url.replace("{transaction_id}",str(trans.id))
                self.redirect(url)

PaypalCancel.register()
