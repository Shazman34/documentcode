from netforce.model import Model,fields,get_model
from netforce import access
from netforce import database
from netforce import utils
from datetime import *
import time
import boto3
import boto3.session
from netforce.utils import json_dumps
import requests
from decimal import *

class Price(Model):
    _name="gt.price"
    _string="Price"
    _name_field="time"
    _fields={
        "time": fields.DateTime("Time",required=True),
        "name": fields.Char("Name",required=True),
        "bid": fields.Decimal("Bid",required=True),
        "ask": fields.Decimal("Ask",required=True),
    }
    _order="id desc"

    def load_prices(self,context={}):
        print("load_prices")
        t=time.strftime("%Y-%m-%d %H:%M:%S")
        url="https://prices.netforce.com/get_prices?_=%s"%t
        req=requests.get(url,timeout=5)
        if req.status_code!=200:
            raise Exception("Invalid status code: %s"%req.status_code)
        min_t=(datetime.now()-timedelta(minutes=1)).strftime("%Y-%m-%d %H:%M:%S")
        db=database.get_connection()
        db.execute("DELETE FROM gt_price")
        data=req.json()
        vals={
            "time": data["time"],
            "name": "spot",
            "bid": data["spot_bid"],
            "ask": data["spot_ask"],
        }
        self.create(vals)
        vals={
            "time": data["time"],
            "name": "usd_thb",
            "bid": data["usd_thb"],
            "ask": data["usd_thb"],
        }
        self.create(vals)
        vals={
            "time": data["time"],
            "name": "cust_96",
            "bid": data["cust_96_bid"],
            "ask": data["cust_96_ask"],
        }
        self.create(vals)
        vals={
            "time": data["time"],
            "name": "cust_99",
            "bid": data["cust_99_bid"],
            "ask": data["cust_99_ask"],
        }
        self.create(vals)
        vals={
            "time": data["time"],
            "name": "cust_96_mini",
            "bid": data["cust_96_mini_bid"],
            "ask": data["cust_96_mini_ask"],
        }
        self.create(vals)

    def get_prices(self,context={}):
        prices={}
        for obj in self.search_browse([]):
            prices[obj.name]=obj
        return {
            "cust_96_bid": prices["cust_96"].bid if "cust_96" in prices else 0,
            "cust_96_ask": prices["cust_96"].ask if "cust_96" in prices else 0,
            "cust_99_bid": prices["cust_99"].bid if "cust_99" in prices else 0,
            "cust_99_ask": prices["cust_99"].ask if "cust_99" in prices else 0,
            "cust_96_mini_bid": prices["cust_96_mini"].bid if "cust_96_mini" in prices else 0,
            "cust_96_mini_ask": prices["cust_96_mini"].ask if "cust_96_mini" in prices else 0,
            "spot_bid": prices["spot"].bid if "spot" in prices else 0,
            "spot_ask": prices["spot"].ask if "spot" in prices else 0,
            "usd_thb_bid": prices["usd_thb"].bid if "usd_thb" in prices else 0,
            "usd_thb_ask": prices["usd_thb"].ask if "usd_thb" in prices else 0,
        }

Price.register()
