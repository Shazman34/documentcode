from netforce.controller import Controller
from netforce.model import get_model
from netforce import database
from netforce import access

class PaymentResponse(Controller):
    _path="/l2g_payment_response"

    def post(self):
        print("#"*80)
        ref=self.get_argument("RefNo")
        print("ref=%s"%ref)
        status=self.get_argument("Status")
        trans_id=self.get_argument("TransId",None)
        auth_code=self.get_argument("AuthCode",None)
        database.set_active_db("nfo_load2go")
        with database.Transaction():
            res=get_model("l2g.booking").search([["number","=",ref]])
            if not res:
                raise Exception("Booking not found: %s"%ref)
            book_id=res[0]
            book=get_model("l2g.booking").browse(book_id)
            if status=="0":
                book.write({"state":"canceled"})
                self.redirect("http://pages.netforce.com/?db=nfo_load2go&page=payment_failed")
                return
            elif status=="1":
                ctx={
                    "trans_id": trans_id,
                    "auth_code": auth_code,
                }
                book.confirm(paid=True,context=ctx)
                self.redirect("http://pages.netforce.com/?db=nfo_load2go&page=payment_success")
            else:
                raise Exception("Invalid status: %s"%status)

PaymentResponse.register()
