from netforce.model import Model,fields,get_model
from netforce import access
from datetime import *
from decimal import *
from dateutil.relativedelta import *
from netforce import utils

class Contact(Model):
    _inherit="contact"
    _fields={
        "g1_com_msg": fields.Decimal("G1 Commission",function="get_g1_com_msg"),
    }

    def get_g1_com_msg(self, ids, context={}):
        vals={}
        d=date.today()
        d0=d.replace(day=15)
        if d0>d:
            d0-=relativedelta(months=1)
        d1=d0+relativedelta(months=1)-timedelta(days=1)
        month0=d0.strftime("%b")
        month1=d1.strftime("%b")
        date_from=d0.strftime("%Y-%m-%d")
        date_to=d1.strftime("%Y-%m-%d")
        cond=[["order_id.date",">=",date_from],["order_id.date","<=",date_to],["state","in",["confirmed","done"]]]
        tot_profit=0
        tot_seller={}
        tot_parent={}
        tot_grand_parent={}
        seller_percent=20
        parent_percent=20
        grand_parent_percent=10
        for line in get_model("sale.order.line").search_browse(cond):
            contact=line.order_id.seller_contact_id
            if not contact:
                continue
            prod=line.product_id
            if not prod:
                continue
            purch_price=prod.purchase_price
            if purch_price:
                profit=(line.unit_price-purch_price)*line.qty
            else:
                profit=(line.unit_price*(obj.default_margin or 0)/100)*line.qty
            tot_profit+=profit
            tot_seller.setdefault(contact.id,0)
            tot_seller[contact.id]+=profit*(seller_percent or 0)/100
            parent=contact.commission_parent_id
            if parent:
                tot_parent.setdefault(parent.id,0)
                tot_parent[parent.id]+=profit*(parent_percent or 0)/100
                g_parent=parent.commission_parent_id
                if g_parent:
                    tot_grand_parent.setdefault(g_parent.id,0)
                    tot_grand_parent[g_parent.id]+=profit*(grand_parent_percent or 0)/100
        for obj in self.browse(ids):
            amt=(tot_seller.get(obj.id) or 0)+(tot_parent.get(obj.id) or 0)+(tot_grand_parent.get(obj.id) or 0)
            vals[obj.id]="Commission from %s 15 to %s 14: THB %s"%(month0,month1,utils.format_money(amt))
        return vals

Contact.register()
