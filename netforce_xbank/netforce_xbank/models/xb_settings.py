from netforce.model import Model,fields,get_model
from netforce import database
import time
import requests
import json

class Settings(Model):
    _name="xb.settings"
    _string="Settings"
    _fields={
        "btc_thb_premium": fields.Decimal("BTC/THB Premium"),
        "btc_thb_discount": fields.Decimal("BTC/THB Discount"),
        "gold96_btc_premium": fields.Decimal("Gold 96%/BTC Premium"),
        "gold96_btc_discount": fields.Decimal("Gold 96%/BTC Discount"),
        "manual_usd_thb_bid": fields.Decimal("Manual USD/THB bid"),
        "manual_usd_thb_ask": fields.Decimal("Manual USD/THB ask"),
        "aws_key": fields.Char("AWS Key"),
        "aws_secret": fields.Char("AWS Secret"),
        "node_ip": fields.Char("Node IP"),
    }

Settings.register()
