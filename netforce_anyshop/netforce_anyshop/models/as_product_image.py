from netforce.model import Model,fields,get_model

class ProductImage(Model):
    _name="as.product.image"
    _fields={
        "product_id": fields.Many2One("as.product","Product",required=True,on_delete="cascade"),
        "sequence": fields.Integer("Sequence"),
        "file": fields.File("File"),
    }

ProductImage.register()
