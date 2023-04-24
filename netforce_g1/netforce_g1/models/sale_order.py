from netforce.model import Model,fields,get_model
from netforce import access
from datetime import *
from decimal import *
from dateutil.relativedelta import *
from netforce import utils

class Sale(Model):
    _inherit="sale.order"
    _fields={
        "g1_com_seller": fields.Decimal("G1 Seller Commission",function="get_g1_com_seller"),
    }

    def get_g1_com_seller(self, ids, context={}):
        vals={}
        for obj in self.browse(ids):
            com_seller=0
            for line in obj.lines:
                prod=line.product_id
                if not prod:
                    continue
                purch_price=prod.purchase_price
                if purch_price:
                    profit=(line.unit_price-purch_price)*line.qty
                else:
                    profit=(line.unit_price*(obj.default_margin or 0)/100)*line.qty
                com_seller+=profit*Decimal(0.2)
            vals[obj.id]=com_seller
        return vals

Sale.register()
