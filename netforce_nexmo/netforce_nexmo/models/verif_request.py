from netforce.model import Model,fields,get_model
from netforce import access
import nexmo

class VerifRequest(Model):
    _inherit="verif.request"

    def start_verif(self,phone,context={}):
        print("start_verif",phone)
        access.set_active_user(1)
        if not phone:
            raise Exception("Missing phone")
        phone=phone.replace(" ","").replace("+","").replace("-","")
        res=get_model("sms.account").search([],order="sequence")
        if not res:
            raise Exception("SMS account not found")
        acc_id=res[0]
        acc=get_model("sms.account").browse(acc_id)
        if acc.skip_verif:
            return {
                "request_id": 1234,
            }
        if not acc.nexmo_api_key:
            raise Exception("Missing Nexmo key")
        if not acc.nexmo_api_secret:
            raise Exception("Missing Nexmo secret")
        client=nexmo.Client(key=acc.nexmo_api_key,secret=acc.nexmo_api_secret)
        print("phone",phone)
        if not acc.sender:
            raise Exception("Missing sender")
        res=client.start_verification(number=phone,brand=acc.sender,next_event_wait=60)
        if res["status"]!="0":
            raise Exception("Failed to start verification: %s"%res["error_text"])
        vals={
            "phone": phone,
            "ref": res["request_id"],
            "state": "sent",
        }
        req_id=self.create(vals)
        return {
            "request_id": req_id,
        }

    def check_verif(self,req_id,code,context={}):
        access.set_active_user(1)
        obj=self.browse(req_id)
        res=get_model("sms.account").search([],order="sequence")
        if not res:
            raise Exception("Voice account not found")
        acc_id=res[0]
        acc=get_model("sms.account").browse(acc_id)
        if acc.skip_verif:
            obj.write({"state":"verified"})
            return
        if not acc.nexmo_api_key:
            raise Exception("Missing Nexmo key")
        if not acc.nexmo_api_secret:
            raise Exception("Missing Nexmo secret")
        client=nexmo.Client(key=acc.nexmo_api_key,secret=acc.nexmo_api_secret)
        res=client.check_verification(obj.ref,code=code)
        if res["status"]!="0":
            raise Exception("Verification failed: %s"%res["error_text"])
        obj.write({"state":"verified"})

VerifRequest.register()
