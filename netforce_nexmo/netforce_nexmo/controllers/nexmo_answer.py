from netforce.controller import Controller
from netforce.model import get_model
from netforce import database
from netforce import access
import json

class Answer(Controller):
    _path="/nexmo_answer"

    def get(self):
        print("@"*80)
        print("@"*80)
        print("@"*80)
        print("nexmo_answer GET")
        dbname=self.get_argument("dbname",None)
        print("dbname",dbname)
        if dbname:
            database.set_active_db(dbname)
        call_id=int(self.get_argument("call_id"))
        call=get_model("voice.call").browse(call_id)
        data=[{
            "action": "talk",
            "text": "Please wait while we connect you",
        },{
            "action": "connect",
            "from": "6531389917", # XXX
            "endpoint": [
              {
                "type": "phone",
                "number": call.phone_to,
              }
            ]
        }]
        self.set_header("Content-Type","application/json")
        self.write(json.dumps(data))

Answer.register()
