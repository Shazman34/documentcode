from netforce.model import Model,fields,get_model
from netforce import access

class ProductCateg(Model):
    _name="as.product.categ"
    _string="Product Category"
    _fields={
        "shop_id": fields.Many2One("as.shop","Shop",required=True),
        "name": fields.Char("Category Name",required=True),
        "parent_id": fields.Many2One("as.product.categ","Parent Category"),
        "color": fields.Char("Color"),
    }
    _order="name,shop_id.name"

    def add_categ(self,vals,context={}):
        access.set_active_user(1)
        categ_vals={
            "name": vals["name"],
            "shop_id": vals["shop_id"],
        }
        categ_id=self.create(vals)
        return {
            "categ_id": categ_id,
        }

    def delete_categ(self,ids,context={}):
        access.set_active_user(1)
        self.delete(ids)

ProductCateg.register()
