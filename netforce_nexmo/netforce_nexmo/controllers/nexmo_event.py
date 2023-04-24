from netforce.controller import Controller
from netforce.model import get_model
from netforce import database
from netforce import access
import json

class Event(Controller):
    _path="/nexmo_event"

    def post(self):
        print("@"*80)
        print("@"*80)
        print("@"*80)
        print("nexmo_event")
        data=json.loads(self.request.body.decode("utf-8"))
        print("data",data)
        dbname=self.get_argument("dbname",None)
        print("dbname",dbname)
        if dbname:
            database.set_active_db(dbname)
        with database.Transaction():
            res=get_model("voice.call").search([["call_id","=",data["uuid"]]])
            if not res:
                raise Exception("Call not found")
            call_id=res[0]
            call=get_model("voice.call").browse(call_id)
            call.write({"state_details":data["status"]})
            if data["status"] in ("completed",):
                call.write({"state":"done"})
            if data["status"] in ("timeout","failed"):
                call.write({"state":"error"})

Event.register()
