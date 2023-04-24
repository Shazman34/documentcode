from netforce.model import Model,fields,get_model
from netforce import access
import time
from decimal import *

class CustMatch(Model):
    _name="gt.cust.match"
    _string="Customer Match"
    _audit_log=True
    _name_field="number"
    _fields={
        "number": fields.Char("Number",required=True,search=True),
        "create_time": fields.DateTime("Create Time",required=True,search=True,readonly=True),
        "customer_id": fields.Many2One("gt.customer","Customer",required=True,search=True),
        "product": fields.Selection([["96","96.5%"],["99","99.99% LBMA"]],"Product",required=True,search=True),
        "num_orders": fields.Integer("# Orders",function="get_order_total",function_multi=True),
        "net_thb": fields.Decimal("Net THB Amount",function="get_order_total",function_multi=True),
        "buy_thb": fields.Decimal("Buy THB Amount",function="get_order_total",function_multi=True),
        "sell_thb": fields.Decimal("Sell THB Amount",function="get_order_total",function_multi=True),
        "buy_96_qty": fields.Decimal("Buy 96.5% Qty",function="get_order_total",function_multi=True),
        "sell_96_qty": fields.Decimal("Sell 96.5% Qty",function="get_order_total",function_multi=True),
        "buy_99_qty": fields.Decimal("Buy 99.99% Qty",function="get_order_total",function_multi=True),
        "sell_99_qty": fields.Decimal("Sell 99.99% Qty",function="get_order_total",function_multi=True),
        "net_96_qty": fields.Decimal("Net 96.5% Qty",function="get_order_total",function_multi=True),
        "net_99_qty": fields.Decimal("Net 99.99% Qty",function="get_order_total",function_multi=True),
        "qty_96": fields.Decimal("96.5% Qty",function="get_order_total",function_multi=True),
        "qty_99": fields.Decimal("99.99% Qty",function="get_order_total",function_multi=True),
        "late_fee_total": fields.Decimal("Late Fee Total",function="get_order_total",function_multi=True),
        "pl_amount": fields.Decimal("P/L Amount",function="get_order_total",function_multi=True),
        "orders": fields.One2Many("gt.cust.order","match_id","Orders"),
        "state": fields.Selection([["waiting_payment","Waiting Payment"],["done","Completed"]],"Order Status",function="get_state"),
        "payment_id": fields.Many2One("gt.cust.payment","Payment"),
    }
    _order="create_time desc"

    def _get_number(self, context={}):
        settings = get_model("gt.settings").browse(1)        
        seq_id = settings.seq_cust_match_id.id
        if not seq_id:
            return None
        while 1:
            num = get_model("sequence").get_next_number(seq_id, context=context)
            if not num:
                return None
            user_id = access.get_active_user()
            access.set_active_user(1)
            res = self.search([["number", "=", num]])
            access.set_active_user(user_id)
            if not res:
                return num
            get_model("sequence").increment_number(seq_id, context=context)

    _defaults={
        "create_time": lambda *a: time.strftime("%Y-%m-%d %H:%M:%S"),
        "number": _get_number,
    }

    def get_order_total(self,ids,context={}):
        vals={}
        for obj in self.browse(ids):
            n=0
            amt=0
            amt_buy=0
            amt_sell=0
            qty_96_buy=0
            qty_96_sell=0
            qty_99_buy=0
            qty_99_sell=0
            late_fee=0
            for order in obj.orders:
                n+=1
                if order.type=="buy":
                    amt-=order.amount
                    amt_buy+=order.amount
                    if order.product=="96":
                        qty_96_buy+=order.qty
                    elif order.product=="99":
                        qty_99_buy+=order.qty
                elif order.type=="sell":
                    amt+=order.amount
                    amt_sell+=order.amount
                    if order.product=="96":
                        qty_96_sell+=order.qty
                    elif order.product=="99":
                        qty_99_sell+=order.qty
                late_fee+=order.late_fee or 0
            vals[obj.id]={
                "num_orders": n,
                "net_thb": amt,
                "buy_thb": amt_buy,
                "pl_amount": amt-late_fee,
                "sell_thb": amt_sell,
                "buy_96_qty": qty_96_buy,
                "sell_96_qty": qty_96_sell,
                "buy_99_qty": qty_99_buy,
                "sell_99_qty": qty_99_sell,
                "net_96_qty": qty_96_buy-qty_96_sell,
                "net_99_qty": qty_99_buy-qty_99_sell,
                "qty_96": qty_96_buy,
                "qty_99": qty_99_buy,
                "late_fee_total": late_fee,
            }
        return vals

    def get_state(self,ids,context={}):
        vals={}
        for obj in self.browse(ids):
            state="done"
            for order in obj.orders:
                if order.state!="done":
                    state="waiting_payment"
            vals[obj.id]=state
        return vals

    def copy_to_payment(self,ids,context={}):
        cust_id=None
        amt=0
        for obj in self.browse(ids):
            for order in obj.orders:
                if order.state not in ("confirmed","matched","done"):
                    raise Exception("Invalid order state")
                if cust_id is None:
                    cust_id=order.customer_id.id
                else:
                    if cust_id!=order.customer_id.id:
                        raise Exception("Orders belong to different customers")
                if order.type=="buy":
                    amt+=order.amount+(order.late_fee or 0)
                elif order.type=="sell":
                    amt-=order.amount-(order.late_fee or 0)
        vals={
            "customer_id": cust_id,
            "direction": amt>0 and "in" or "out",
            "amount": abs(amt),
        }
        pmt_id=get_model("gt.cust.payment").create(vals)
        for obj in self.browse(ids):
            obj.write({"payment_id": pmt_id})
            for order in obj.orders:
                order.write({"payment_id": pmt_id})
        return {
            "next": {
                "name": "gt_cust_payment",
                "mode": "form",
                "active_id": pmt_id,
            },
        }

CustMatch.register()
