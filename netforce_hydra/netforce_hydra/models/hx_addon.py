from netforce.model import Model,fields,get_model
from netforce import database
from netforce import access
from netforce import utils
import time
import random

class Addon(Model):
    _name="hx.addon"
    _string="Add-on"
    _fields={
        "sequence": fields.Integer("Sequence"),
        "name": fields.Char("Add-On Name",required=True),
        "title": fields.Char("Title",required=True),
        "version": fields.Char("Version"),
        "plans": fields.Many2Many("hx.plan","Plans"),
        "description": fields.Text("Description"),
        "file": fields.File("ZIP file"),
    }
    _order="sequence,name"

    def get_filter(self,*args,**kw):
        user_id=access.get_active_user()
        if user_id==1:
            return True
        user=get_model("base.user").browse(user_id)
        return ["plans.id","=",user.hx_plan_id.id]

    def install(self,name,context={}):
        user_id=access.get_active_user()
        if not user_id:
            raise Exception("Not logged in")
        user=get_model("base.user").browse(user_id)
        plan_id=user.hx_plan_id.id
        if not plan_id:
            raise Exception("Missing plan")
        res=self.search([["name","=",name]])
        if not res:
            raise Exception("Addon not found: %s"%name)
        obj_id=res[0]
        obj=self.browse(obj_id)
        plan_ids=[p.id for p in obj.plans]
        if plan_id not in plan_ids:
            raise Exception("This addon is not included in your current price plan (%s)."%user.hx_plan_id.name)
        if not obj.file:
            raise Exception("Missing ZIP file")
        base_url="https://backend.netforce.com/static/db/nfo_hydra/files/"
        url=base_url+"/"+obj.file
        return {
            "url": url,
            "version": obj.version, 
        }

Addon.register()
