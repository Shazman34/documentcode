from netforce.model import Model, fields, get_model
from netforce import access
from netforce import config
from netforce import utils
import time
import requests
import hashlib
import hmac
import json

class Product(Model):
    _inherit = "product"
    _fields = {
        "lazada_details": fields.One2Many("product.lazada.details","product_id","Lazada Details"),
        "lazada_sync_stock": fields.Boolean("Lazada Sync Stock On"),
        "sync_records": fields.One2Many("sync.record","related_id","Sync Records"),
    }


    def update_lazada_stock(self,ids,context={}):
        print("Update Lazada Stock",ids)
        pass

    def update_lazada_stock_async(self,ids,context={}):
        vals={
            "date": time.strftime("%Y-%m-%d %H:%M:%S"),
            "model": "product",
            "method": "update_lazada_stock",
            "args": json.dumps({
                "ids": ids,
            }),
        }
        get_model("bg.task").create(vals)

Product.register()
