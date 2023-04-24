from netforce.model import Model,fields,get_model
from netforce import ipc


class Addon(Model):
    _name="addon"
    _string="Addon"
    _fields={
        "name": fields.Char("Addon Name",required=True,search=True),
        "code": fields.Char("Addon Code"),
        "price": fields.Decimal("Base Price (USD per month)",required=True),
        "plan_price": fields.Decimal("Extra Price (USD per month)",function="get_plan_price"),
        "description": fields.Text("Description"),
        "state": fields.Selection([["not_installed","Not Installed"],["installed","Installed"]],"Status",required=True,search=True),
        "sequence": fields.Integer("Sequence"),
        "price_plans": fields.Many2Many("price.plan","Included In Price Plans"),
    }
    _order="sequence"
    _defaults={
        "state": "not_installed",
    }

    def get_plan_price(self,ids,context={}):
        settings=get_model("settings").browse(1)
        if settings.bill_plan_id:
            addon_ids=[a.id for a in settings.bill_plan_id.addons]
        else:
            addon_ids=[]
        vals={}
        for obj in self.browse(ids):
            vals[obj.id]=obj.price if obj.id not in addon_ids else 0
        return vals

    def install_addon(self,ids,context={}):
        for obj in self.browse(ids):
            obj.write({"state":"installed"})
        ipc.send_signal("clear_ui_params_cache")
        return {
            "next": {
                "type": "reload",
            }
        }

    def uninstall_addon(self,ids,context={}):
        for obj in self.browse(ids):
            obj.write({"state":"not_installed"})
        ipc.send_signal("clear_ui_params_cache")
        return {
            "next": {
                "type": "reload",
            }
        }

    def addons_to_json(self,context={}):
        addons=[]
        for obj in self.search_browse([["state","=","installed"]]):
            addons.append(obj.code)
        return addons

Addon.register()   
