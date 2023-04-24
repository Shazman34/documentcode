from netforce.model import Model,fields,get_model
from netforce import database
import nexmo

class Call(Model):
    _inherit="voice.call"

    def start_call(self,ids,context={}):
        print("Call.start_call")
        obj=self.browse(ids[0])
        res=get_model("voice.account").search([],order="sequence")
        if not res:
            raise Exception("Voice account not found")
        acc_id=res[0]
        acc=get_model("voice.account").browse(acc_id)
        if not acc.nexmo_app_id:
            raise Exception("Missing Nexmo app ID")
        if not acc.nexmo_private_key:
            raise Exception("Missing Nexmo private key")
        client=nexmo.Client(application_id=acc.nexmo_app_id,private_key=acc.nexmo_private_key)
        if not acc.nexmo_phone:
            raise Exception("Missing Nexmo phone")
        dbname=database.get_active_db()
        res = client.create_call({
            'to': [{'type': 'phone', 'number': obj.phone_from}],
            'from': {'type': 'phone', 'number': acc.nexmo_phone},
            'answer_url': ['https://backend.netforce.com/nexmo_answer?dbname=%s&call_id=%d'%(dbname,obj.id)],
        })
        print("Nexmo response",res)
        obj.write({"call_id":res["uuid"],"state_details":res["status"],"state":"in_progress"})

Call.register()
