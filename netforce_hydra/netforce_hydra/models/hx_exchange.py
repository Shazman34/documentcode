from netforce.model import Model,fields,get_model
from netforce import database
from netforce import access
from netforce import utils
import time
import random

class Exchange(Model):
    _name="hx.exchange"
    _string="Exchange"
    _fields={
        "sequence": fields.Integer("Sequence"),
        "name": fields.Char("Exchange Name",required=True,search=True),
        "code": fields.Char("Code",required=True),
        "countries": fields.Char("Countries"),
        "logo_url": fields.Char("Logo URL"),
        "plans": fields.Many2Many("hx.plan","Plans"),
        "allow_cors": fields.Boolean("Allow CORS",search=True),
    }
    _order="name"

    def get_filter(self,*args,**kw):
        user_id=access.get_active_user()
        if user_id==1:
            return True
        user=get_model("base.user").browse(user_id)
        return ["plans.id","=",user.hx_plan_id.id]

Exchange.register()
