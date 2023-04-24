from netforce.controller import Controller
from netforce.model import get_model
from netforce import database
from netforce import access
import json
import time

class UploadLoc(Controller):
    _path="/l2g_upload_loc"

    def get(self):
        print("UploadLoc GET")

    def post(self):
        print("L"*80)
        print("L"*80)
        print("L"*80)
        print("UploadLoc POST")
        print("body",self.request.body)
        database.set_active_db("nfo_load2go")
        with database.Transaction():
            res=json.loads(self.request.body.decode("utf-8"))
            data=res[0]
            driver_id=int(data["driver_id"])
            lat=data["lat"]
            lng=data["lng"]
            coords="%s,%s"%(lat,lng)
            t=time.strftime("%Y-%m-%d %H:%M:%S")
            db=database.get_connection()
            db.execute("INSERT INTO l2g_loc_update (time,driver_id,coords) VALUES (%s,%s,%s)",t,driver_id,coords)

UploadLoc.register()
