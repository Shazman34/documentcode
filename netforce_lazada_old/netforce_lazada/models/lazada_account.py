from netforce.model import Model, fields, get_model
from netforce import config
from netforce import utils
from netforce import database
import requests
import hashlib
import hmac
from datetime import *
import time

class Account(Model):
    _name = "lazada.account"
    _string = "Lazada Account"
    _fields = {
        "name": fields.Char("Shop Name",required=True,search=True),
        "shop_idno": fields.Char("Shop ID",search=True),
        "auth_code": fields.Char("Auth Code"),
        "region": fields.Char("Region"),
        "status": fields.Char("Status"),
        "token": fields.Char("Token"),
        "refresh_token": fields.Char("Refresh Token"),
        "sale_channel_id": fields.Many2One("sale.channel","Sales Channel"),
        "sync_records": fields.One2Many("sync.record","account_id","Sync Records"),
    }

Account.register()
