from netforce.model import Model,fields,get_model
from netforce import access
import time

class ShopUser(Model):
    _name="as.shop.user"
    _string="Shop User"
    _fields={
        "date_add": fields.DateTime("Date Added",required=True,search=True),
        "shop_id": fields.Many2One("as.shop","Shop"),
        "device_id": fields.Many2One("as.device","Device"),
        "search_q": fields.Char("Search",store=False,function_search="get_search_q"),
    }
    _defaults={
        "date_add": lambda *a: time.strftime("%Y-%m-%d %H:%M:%S"),
    }
    _order="date_add desc"

    def scan_shop_code(self,device_id,code,context={}):
        access.set_active_user(1)
        res=get_model("as.shop").search([["name","=",code]])
        if not res:
            raise Exception("Invalid shop code: %s"%code)
        shop_id=res[0]
        res=self.search([["shop_id","=",shop_id],["device_id","=",device_id]])
        if res:
            raise Exception("Shop already added: %s"%code)
        vals={
            "device_id": device_id,
            "shop_id": shop_id,
        }
        self.create(vals)

    def get_search_q(self,clause,context={}):
        q=clause[2]
        return [["shop_id.name","ilike",q]]

ShopUser.register()
