from netforce.model import Model,fields,get_model
from netforce import access
import time

class Shop(Model):
    _name="as.shop"
    _string="Shop"
    _name_field="name"
    _fields={
        "date_add": fields.DateTime("Date Added",required=True,search=True),
        "name": fields.Char("Shop Name",required=True,search=True),
        "city_id": fields.Many2One("as.city","City"),
        "description": fields.Text("Description"),
        "photo": fields.File("Photo"),
        "user_id": fields.Many2One("as.user","Owner",required=True),
        "products": fields.One2Many("as.product","shop_id","Products"),
        "search_q": fields.Char("Search",store=False,function_search="get_search_q"),
        "website": fields.Char("Website"),
        "color": fields.Char("Color"),
        "users": fields.One2Many("as.shop.user","shop_id","Users"),
        "code": fields.Char("Shop Code"),
    }
    _defaults={
        "date_add": lambda *a: time.strftime("%Y-%m-%d %H:%M:%S"),
    }
    _order="date_add desc"

    def add_shop(self,vals,context={}):
        access.set_active_user(1)
        shop_vals={
            "user_id": vals["user_id"],
            "name": vals["name"],
        }
        shop_id=self.create(shop_vals)
        return {
            "shop_id": shop_id,
        }

    def update_shop(self,shop_id,vals,context={}):
        access.set_active_user(1)
        self.write([shop_id],vals)

    def get_search_q(self,clause,context={}):
        q=clause[2]
        return [["name","ilike",q]]

Shop.register()
