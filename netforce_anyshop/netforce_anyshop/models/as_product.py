from netforce.model import Model,fields,get_model
from netforce import access
import time

class Product(Model):
    _name="as.product"
    _string="Product"
    _fields={
        "date_add": fields.DateTime("Date Added",required=True,search=True),
        "shop_id": fields.Many2One("as.shop","Shop",required=True,search=True),
        "categ_id": fields.Many2One("as.product.categ","Product Category",search=True),
        "categ_color": fields.Char("Categ Color",function="_get_related",function_context={"path":"categ_id.color"}),
        "name": fields.Char("Product Title",required=True,search=True),
        "condition": fields.Selection([["new","New"],["used","Used"]],"Condition"),
        "description": fields.Text("Description"),
        "sale_price": fields.Decimal("Sales Price",required=True,search=True),
        "allow_meetup": fields.Boolean("Allow Meet-up"),
        "meetup_coords": fields.Char("Meet-up coordinates"),
        "meetup_details": fields.Text("Meet-up details"),
        "allow_delivery": fields.Boolean("Allow Delivery"),
        "delivery_details": fields.Text("Delivery details"),
        "images": fields.One2Many("as.product.image","product_id","Images"),
        "image": fields.File("Image",function="get_image"),
        "search_q": fields.Char("Search",store=False,function_search="get_search_q"),
    }
    _defaults={
        "date_add": lambda *a: time.strftime("%Y-%m-%d %H:%M:%S"),
    }
    _order="name"

    def get_image(self,ids,context={}):
        vals={}
        for obj in self.browse(ids):
            vals[obj.id]=obj.images[0].file if obj.images else None
        return vals

    def submit_product(self,vals,context={}):
        access.set_active_user(1)
        if not vals.get("shop_id"):
            raise Exception("Missing shop ID")
        has_pic=False
        for i in range(4):
            if vals.get("pic_%d"%i):
                has_pic=True
                break
        if not has_pic:
            raise Exception("Missing photo")
        if not vals.get("name"):
            raise Exception("Missing product title")
        if not vals.get("price"):
            raise Exception("Missing price")
        if not vals.get("categ_id"):
            raise Exception("Missing category")
        prod_vals={
            "shop_id": vals["shop_id"],
            "name": vals["name"],
            "sale_price": vals["price"],
            "description": vals.get("description"),
            "categ_id": vals.get("categ_id"),
            "images": [("delete_all",)],
        }
        seq=1
        for i in range(4):
            if vals.get("pic_%d"%i):
                prod_vals["images"].append(("create",{"sequence":seq,"file":vals["pic_%d"%i]}))
                seq+=1
        prod_id=vals.get("product_id")
        if prod_id:
            get_model("as.product").write([prod_id],prod_vals)
        else:
            prod_id=get_model("as.product").create(prod_vals)
        return {
            "product_id": prod_id,
        }

    def delete_product(self,ids,context={}):
        access.set_active_user(1)
        self.delete(ids)

    def get_search_q(self,clause,context={}):
        q=clause[2]
        return ["or",["name","ilike",q],["description","ilike",q]]

Product.register()
