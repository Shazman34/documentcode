from netforce.model import Model, fields, get_model
from netforce import database
from netforce import access
from netforce import config
from netforce import utils
import time
import requests
import hashlib
import hmac


class Move(Model):
    _inherit = "stock.move"

    def update_balance(self,ids,context={}):
        if not ids:
            return
        super().update_balance(ids,context)
        try:
            lazada_settings = get_model("lazada.settings").browse(1)
            if not lazada_settings or not lazada_settings.check_stock:
                return
            db=database.get_connection()
            res=db.query("SELECT p.id product_id, p.lazada_sync_stock sync FROM stock_move sm LEFT JOIN product p ON sm.product_id=p.id WHERE sm.id IN %s",tuple(ids))
            prod_ids=[r.product_id for r in res if r.sync]
            prod_ids=list(set(prod_ids))
            if prod_ids:
                get_model("product").update_lazada_stock_async(prod_ids)
        except:
            pass

Move.register()
