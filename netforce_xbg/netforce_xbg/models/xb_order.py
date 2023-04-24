from netforce.model import Model, fields, get_model
from netforce import database
from datetime import *
import time, requests, json, random, hashlib

BX_KEY = 'b5020318838c'
BX_SECRET = '3a06b69958dc'

class Order(Model):
    _name = 'xb.order'
    _string = 'Order'
    _fields = {
        'date_created': fields.DateTime('Date Created', required=True),
     'number': fields.Char('Order Number', required=True),
     'currency': fields.Selection([['btc', 'BTC'], ['eth', 'ETH']], 'Currency', required=True),
     'amount': fields.Decimal('Payment Amount', scale=6, required=True),
     'price': fields.Decimal('Gold Price', scale=6, required=True),
     'qty': fields.Decimal('Gold Qty', scale=3, required=True),
     'email': fields.Char('Email', required=True),
     'address': fields.Char('Address', required=True),
     "account_id": fields.Many2One("xb.account","Account"),
     "side": fields.Selection([["buy","Buy"],["sell","Sell"]],"Side",required=True),
     "state": fields.Selection([["pending","Pending"],["done","Completed"],["canceled","Canceled"]],"Status",required=True),
     }

    def _get_number(self, context):
        n = random.randint(0, 1000000)
        return 'XO-%.6d' % n

    _defaults = {
        'date_created': lambda *a: time.strftime('%Y-%m-%d %H:%M:%S'),
        'number': _get_number,
        "state": "pending",
     }
    _order = 'date_created'

    def new_deposit_addr(self, currency):
        params = {
            'key': BX_KEY,
             'nonce': int(time.time() * 1000),
             'currency': currency,
         }
        params['signature'] = hashlib.sha256((params['key'] + str(params['nonce']) + BX_SECRET).encode('utf-8')).hexdigest()
        print('params', params)
        url = 'https://bx.in.th/api/deposit/'
        r = requests.post(url, data=params)
        try:
            res = r.json()
        except:
            raise Exception('Failed to get deposit address: status code %s' % r.status_code)

        print('BX response', res)
        addr = res.get('address')
        if not addr:
            raise Exception('Failed to get deposit address')
        return addr

    def place_order(self, vals, context={}):
        print('place_order', vals)
        currency = vals['currency']
        addr = self.new_deposit_addr(currency)
        vals['address'] = addr
        email=vals.get("email")
        if email:
            res=get_model("xb.account").search([["email","=",email]])
            if res:
                acc_id=res[0]
                vals["account_id"]=acc_id
        new_id = self.create(vals)
        res = self.read([new_id])
        data = res[0]
        return {
            'order_data': data
         }

Order.register()
