from netforce.model import Model,fields,get_model
import nexmo

class Message(Model):
    _inherit="sms.message"

    def send_nexmo(self,ids,context={}):
        obj=self.browse(ids[0])
        try:
            acc=obj.account_id
            if not acc.nexmo_api_key:
                raise Exception("Missing Nexmo API key")
            if not acc.nexmo_api_secret:
                raise Exception("Missing Nexmo API secret")
            if not acc.sender:
                raise Exception("Missing sender")
            client = nexmo.Client(key=acc.nexmo_api_key, secret=acc.nexmo_api_secret)
            res=client.send_message({
                "from": acc.sender,
                "to": obj.phone,
                "text": obj.body,
            })
            res=res["messages"][0]
            if res["status"]!="0":
                raise Exception("Failed to send SMS: %s"%res["error-text"])
            obj.write({"state": "sent"})
        except Exception as e:
            obj.write({"state": "error"})
            obj.write({"state": "error","error":str(e)})

Message.register()
