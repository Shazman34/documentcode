from netforce.model import Model,fields,get_model
from netforce import access
import time

class Device(Model):
    _name="as.device"
    _string="Device"
    _name_field="code"
    _fields={
        "date_add": fields.DateTime("Date Added",required=True,search=True),
        "code": fields.Char("Code",required=True,search=True),
        "model": fields.Char("Model",search=True),
        "shops": fields.One2Many("as.shop.user","device_id","Shops"),
    }
    _defaults={
        "date_add": lambda *a: time.strftime("%Y-%m-%d %H:%M:%S"),
    }
    _order="date_add desc"

    def add_device(self,vals,context={}):
        access.set_active_user(1)
        code=vals["code"]
        res=self.search([["code","=",code]])
        if res:
            dev_id=res[0]
        else:
            dev_id=self.create(vals)
        return {
            "device_id": dev_id,
        }

Device.register()
