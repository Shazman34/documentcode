from netforce.model import Model, fields, get_model
from netforce import access
import time


class SyncRecord(Model):
    _name = "sync.record"
    _fields = {
        "related_id": fields.Reference([["product","Product"],["sale.order","Sales Order"],["stock.picking","Stock Picking"],["lazada.order","Lazada Order"]],"Related To",required=True),
        "sync_id": fields.Char("Sync ID",required=True),
        "time": fields.DateTime("Sync Time",required=True),
        "account_id": fields.Reference([["lazada.account","Lazada"]],"Account",required=True),
    }
    _defaults={
        "time": lambda *a: time.strftime("%Y-%m-%d %H:%M:%S"),
    }
    _order="id desc"

SyncRecord.register()
