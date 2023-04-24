from netforce.model import Model,fields,get_model
from netforce import database
from netforce import utils
from netforce import access
from decimal import *
from datetime import *
import time
import random

class Customer(Model):
    _name="gt.customer"
    _string="Customer"
    _audit_log=True
    _fields={
        "number": fields.Char("Number",required=True,search=True),
        "create_time": fields.DateTime("Create Time",required=True,search=True,readonly=True),
        "name": fields.Char("Customer Name",required=True,search=True), 
        "email": fields.Char("Email"),
        "phone": fields.Char("Phone"),
        "categ_id": fields.Many2One("gt.cust.categ","Customer Category",required=True),
        "orders": fields.One2Many("gt.cust.order","customer_id","Orders"),
        "payments": fields.One2Many("gt.cust.payment","customer_id","Payments"),
        "deliveries": fields.One2Many("gt.cust.delivery","customer_id","Deliveries"),
        "deposits": fields.One2Many("gt.cust.deposit","customer_id","Deposits"),
        "min_margin": fields.Decimal("Min Margin (%)",function="_get_related",function_context={"path":"categ_id.min_margin"}),
        "margin": fields.Decimal("Current Margin (%)",function="get_margin",function_multi=True),
        "margin_eq": fields.Decimal("Margin Equity",function="get_margin",function_multi=True),
        "margin_mkt": fields.Decimal("Margin Market Value",function="get_margin",function_multi=True),
        "dep_thb": fields.Decimal("Deposit THB",function="get_deposit",function_multi=True),
        "dep_96": fields.Decimal("Deposit 96.5%",function="get_deposit",function_multi=True),
        "dep_96_thb": fields.Decimal("Deposit 96.5% Value",function="get_deposit",function_multi=True),
        "dep_99": fields.Decimal("Deposit 99.99%",function="get_deposit",function_multi=True),
        "dep_99_thb": fields.Decimal("Deposit 99.99% Value",function="get_deposit",function_multi=True),
        "bal_thb": fields.Decimal("Balance THB",function="get_balance",function_multi=True),
        "bal_96": fields.Decimal("Balance 96.5%",function="get_balance",function_multi=True),
        "bal_96_thb": fields.Decimal("Balance 96.5% Value",function="get_balance",function_multi=True),
        "bal_99": fields.Decimal("Balance 99.99%",function="get_balance",function_multi=True),
        "bal_99_thb": fields.Decimal("Balance 99.99% Value",function="get_balance",function_multi=True),
        "lim_buy_96": fields.Decimal("Limit Buy 96.5%",function="get_limit",function_multi=True),
        "lim_sell_96": fields.Decimal("Limit Sell 96.5%",function="get_limit",function_multi=True),
        "lim_buy_99": fields.Decimal("Limit Buy 99.99%",function="get_limit",function_multi=True),
        "lim_sell_99": fields.Decimal("Limit Sell 99.99%",function="get_limit",function_multi=True),
        "qtys_buy_96": fields.Json("Order Qtys 96.5% Buy",function="get_order_qtys",function_multi=True),
        "qtys_sell_96": fields.Json("Order Qtys 96.5% Sell",function="get_order_qtys",function_multi=True),
        "qtys_buy_99": fields.Json("Order Qtys 99.99% Buy",function="get_order_qtys",function_multi=True),
        "qtys_sell_99": fields.Json("Order Qtys 99.99% Sell",function="get_order_qtys",function_multi=True),
        "qtys_buy_96_mini": fields.Json("Order Qtys 96.5% MINI Buy",function="get_order_qtys",function_multi=True),
        "qtys_sell_96_mini": fields.Json("Order Qtys 96.5% MINI Sell",function="get_order_qtys",function_multi=True),
        "late_pay_fee": fields.Decimal("Late Payment Fee (THB/baht/day)",function="_get_related",function_context={"path":"categ_id.late_pay_fee"}),
        "conf_buy_96_qty": fields.Decimal("Conf. 96.5% Buy Qty",function="get_conf",function_multi=True),
        "conf_buy_96_avg": fields.Decimal("Conf. 96.5% Buy Avg",function="get_conf",function_multi=True),
        "conf_buy_96_amt": fields.Decimal("Conf. 96.5% Buy Total",function="get_conf",function_multi=True),
        "conf_sell_96_qty": fields.Decimal("Conf. 96.5% Sell Qty",function="get_conf",function_multi=True),
        "conf_sell_96_avg": fields.Decimal("Conf. 96.5% Sell Avg",function="get_conf",function_multi=True),
        "conf_sell_96_amt": fields.Decimal("Conf. 96.5% Sell Total",function="get_conf",function_multi=True),
        "conf_net_96_qty": fields.Decimal("Conf. 96.5% Net Qty",function="get_conf",function_multi=True),
        "conf_net_96_amt": fields.Decimal("Conf. 96.5% Net Total",function="get_conf",function_multi=True),
        "conf_buy_99_qty": fields.Decimal("Conf. 99.99% Buy Qty",function="get_conf",function_multi=True),
        "conf_buy_99_avg": fields.Decimal("Conf. 99.99% Buy Avg",function="get_conf",function_multi=True),
        "conf_buy_99_avg_bg": fields.Decimal("Conf. 99.99% Buy Avg (bg)",function="get_conf",function_multi=True),
        "conf_buy_99_amt": fields.Decimal("Conf. 99.99% Buy Total",function="get_conf",function_multi=True),
        "conf_sell_99_qty": fields.Decimal("Conf. 99.99% Sell Qty",function="get_conf",function_multi=True),
        "conf_sell_99_avg": fields.Decimal("Conf. 99.99% Sell Avg",function="get_conf",function_multi=True),
        "conf_sell_99_avg_bg": fields.Decimal("Conf. 99.99% Sell Avg (bg)",function="get_conf",function_multi=True),
        "conf_sell_99_amt": fields.Decimal("Conf. 99.99% Sell Total",function="get_conf",function_multi=True),
        "conf_net_99_qty": fields.Decimal("Conf. 99.99% Net Qty",function="get_conf",function_multi=True),
        "conf_net_99_amt": fields.Decimal("Conf. 99.99% Net Total",function="get_conf",function_multi=True),
        "match_net_96_qty": fields.Decimal("Match 96.5% Net Qty",function="get_match",function_multi=True),
        "match_net_96_amt": fields.Decimal("Match 96.5% Net Total",function="get_match",function_multi=True),
        "match_net_99_qty": fields.Decimal("Match 99.99% Net Qty",function="get_match",function_multi=True),
        "match_net_99_amt": fields.Decimal("Match 99.99% Net Total",function="get_match",function_multi=True),
        "done_net_96_qty": fields.Decimal("Completed 96.5% Net Qty",function="get_done",function_multi=True),
        "done_net_96_amt": fields.Decimal("Completed 96.5% Net Total",function="get_done",function_multi=True),
        "done_net_99_qty": fields.Decimal("Completed 99.99% Net Qty",function="get_done",function_multi=True),
        "done_net_99_amt": fields.Decimal("Completed 99.99% Net Total",function="get_done",function_multi=True),
        "match_profit": fields.Decimal("Realized Profit From Matched Orders",function="get_match_profit"),
        "fake_deposit": fields.Decimal("Fake Deposit (THB)"),
        "users": fields.One2Many("base.user","gt_customer_id","Users"),
        "refer_broker": fields.Char("Introducing Broker"),
        "bank_accounts": fields.One2Many("bank.account","related_id","Bank Accounts"),
        "address": fields.Text("Address"),
    }
    _order="create_time desc"

    def _get_number(self, context={}):
        settings = get_model("gt.settings").browse(1)        
        seq_id = settings.seq_cust_id.id
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

    def get_deposit(self, ids, context={}):
        prices=get_model("gt.price").get_prices()
        vals={}
        for obj in self.browse(ids):
            dep_thb=0
            dep_96=0
            dep_99=0
            for dep in obj.deposits:
                if dep.state!="done":
                    continue
                if dep.direction=="in":
                    if dep.type=="cash":
                        dep_thb+=dep.amount
                    elif dep.type=="gold":
                        if dep.product=="96":
                            dep_96+=dep.qty
                        elif dep.product=="99":
                            dep_99+=dep.qty
                elif dep.direction=="out":
                    if dep.type=="cash":
                        dep_thb-=dep.amount
                    elif dep.type=="gold":
                        if dep.product=="96":
                            dep_96-=dep.qty
                        elif dep.product=="99":
                            dep_99-=dep.qty
            vals[obj.id]={
                "dep_thb": dep_thb,
                "dep_96": dep_96,
                "dep_96_thb": dep_96*prices["cust_96_bid"],
                "dep_99": dep_99,
                "dep_99_thb": dep_99*Decimal(65.6)*prices["cust_99_bid"],
            }
        return vals

    def get_balance(self, ids, context={}):
        prices=get_model("gt.price").get_prices()
        vals={}
        for obj in self.browse(ids):
            bal_thb=0
            bal_96=0
            bal_99=0
            for pmt in obj.payments:
                if pmt.state!="done":
                    continue
                if pmt.direction=="in":
                    bal_thb+=pmt.amount_total
                elif pmt.direction=="out":
                    bal_thb-=pmt.amount_total
            for deliv in obj.deliveries:
                if deliv.state!="done":
                    continue
                if deliv.direction=="in":
                    for line in deliv.lines:
                        if line.product=="96":
                            bal_96+=line.qty
                        elif line.product=="99":
                            bal_99+=line.qty
                elif deliv.direction=="out":
                    for line in deliv.lines:
                        if line.product=="96":
                            bal_96-=line.qty
                        elif line.product=="99":
                            bal_99-=line.qty
            for order in obj.orders:
                if order.state!="done":
                    continue
                if order.type=="buy":
                    bal_thb-=order.amount+(order.late_fee or 0)
                    if order.product in ("96","96_mini"):
                        bal_96+=order.qty
                    elif order.product=="99":
                        bal_99+=order.qty
                elif order.type=="sell":
                    bal_thb+=order.amount-(order.late_fee or 0)
                    if order.product in ("96","96_mini"):
                        bal_96-=order.qty
                    elif order.product=="99":
                        bal_99-=order.qty
            vals[obj.id]={
                "bal_thb": bal_thb,
                "bal_96": bal_96,
                "bal_96_thb": bal_96*prices["cust_96_bid"],
                "bal_99": bal_99,
                "bal_99_thb": bal_99*Decimal(65.6)*prices["cust_99_bid"],
            }
        return vals

    def get_conf(self, ids, context={}):
        vals={}
        for obj in self.browse(ids):
            qtys={}
            amts={}
            for order in obj.orders:
                if order.state!="confirmed":
                    continue
                k=(order.type,order.product)
                qtys.setdefault(k,0)
                qtys[k]+=order.qty
                amts.setdefault(k,0)
                amts[k]+=order.amount
            res={
                "conf_buy_96_qty": qtys.get(("buy","96"),0),
                "conf_buy_96_amt": amts.get(("buy","96"),0),
                "conf_sell_96_qty": qtys.get(("sell","96"),0),
                "conf_sell_96_amt": amts.get(("sell","96"),0),
                "conf_buy_99_qty": qtys.get(("buy","99"),0),
                "conf_buy_99_amt": amts.get(("buy","99"),0),
                "conf_sell_99_qty": qtys.get(("sell","99"),0),
                "conf_sell_99_amt": amts.get(("sell","99"),0),
            }
            res["conf_buy_96_avg"]=round(res["conf_buy_96_amt"]/res["conf_buy_96_qty"]) if res["conf_buy_96_qty"] else None
            res["conf_sell_96_avg"]=round(res["conf_sell_96_amt"]/res["conf_sell_96_qty"]) if res["conf_sell_96_qty"] else None
            res["conf_net_96_qty"]=res["conf_buy_96_qty"]-res["conf_sell_96_qty"]
            res["conf_net_96_amt"]=res["conf_sell_96_amt"]-res["conf_buy_96_amt"]
            res["conf_buy_99_avg"]=round(res["conf_buy_99_amt"]/res["conf_buy_99_qty"]) if res["conf_buy_99_qty"] else None
            res["conf_buy_99_avg_bg"]=round(res["conf_buy_99_amt"]/res["conf_buy_99_qty"]/Decimal(65.6)) if res["conf_buy_99_qty"] else None
            res["conf_sell_99_avg"]=round(res["conf_sell_99_amt"]/res["conf_sell_99_qty"]) if res["conf_sell_99_qty"] else None
            res["conf_sell_99_avg_bg"]=round(res["conf_sell_99_amt"]/res["conf_sell_99_qty"]/Decimal(65.6)) if res["conf_sell_99_qty"] else None
            res["conf_net_99_qty"]=res["conf_buy_99_qty"]-res["conf_sell_99_qty"]
            res["conf_net_99_amt"]=res["conf_sell_99_amt"]-res["conf_buy_99_amt"]
            vals[obj.id]=res
        return vals

    def get_match(self, ids, context={}):
        vals={}
        for obj in self.browse(ids):
            qtys={}
            amts={}
            for order in obj.orders:
                if order.state!="matched":
                    continue
                k=(order.type,order.product)
                qtys.setdefault(k,0)
                qtys[k]+=order.qty
                amts.setdefault(k,0)
                amts[k]+=order.amount
            res={
                "match_buy_96_qty": qtys.get(("buy","96"),0),
                "match_buy_96_amt": amts.get(("buy","96"),0),
                "match_sell_96_qty": qtys.get(("sell","96"),0),
                "match_sell_96_amt": amts.get(("sell","96"),0),
                "match_buy_99_qty": qtys.get(("buy","99"),0),
                "match_buy_99_amt": amts.get(("buy","99"),0),
                "match_sell_99_qty": qtys.get(("sell","99"),0),
                "match_sell_99_amt": amts.get(("sell","99"),0),
            }
            res2={}
            res["match_buy_96_avg"]=round(res["match_buy_96_amt"]/res["match_buy_96_qty"]) if res["match_buy_96_qty"] else None
            res["match_sell_96_avg"]=round(res["match_sell_96_amt"]/res["match_sell_96_qty"]) if res["match_sell_96_qty"] else None
            res2["match_net_96_qty"]=res["match_buy_96_qty"]-res["match_sell_96_qty"]
            res2["match_net_96_amt"]=res["match_sell_96_amt"]-res["match_buy_96_amt"]
            res["match_buy_99_avg"]=round(res["match_buy_99_amt"]/res["match_buy_99_qty"]) if res["match_buy_99_qty"] else None
            res["match_sell_99_avg"]=round(res["match_sell_99_amt"]/res["match_sell_99_qty"]) if res["match_sell_99_qty"] else None
            res2["match_net_99_qty"]=res["match_buy_99_qty"]-res["match_sell_99_qty"]
            res2["match_net_99_amt"]=res["match_sell_99_amt"]-res["match_buy_99_amt"]
            vals[obj.id]=res2
        return vals

    def get_done(self, ids, context={}):
        vals={}
        for obj in self.browse(ids):
            qtys={}
            amts={}
            for order in obj.orders:
                if order.state!="done":
                    continue
                k=(order.type,order.product)
                qtys.setdefault(k,0)
                qtys[k]+=order.qty
                amts.setdefault(k,0)
                amts[k]+=order.amount
            res={
                "done_buy_96_qty": qtys.get(("buy","96"),0),
                "done_buy_96_amt": amts.get(("buy","96"),0),
                "done_sell_96_qty": qtys.get(("sell","96"),0),
                "done_sell_96_amt": amts.get(("sell","96"),0),
                "done_buy_99_qty": qtys.get(("buy","99"),0),
                "done_buy_99_amt": amts.get(("buy","99"),0),
                "done_sell_99_qty": qtys.get(("sell","99"),0),
                "done_sell_99_amt": amts.get(("sell","99"),0),
            }
            res2={}
            res["done_buy_96_avg"]=res["done_buy_96_amt"]/res["done_buy_96_qty"] if res["done_buy_96_qty"] else None
            res["done_sell_96_avg"]=res["done_sell_96_amt"]/res["done_sell_96_qty"] if res["done_sell_96_qty"] else None
            res2["done_net_96_qty"]=res["done_buy_96_qty"]-res["done_sell_96_qty"]
            res2["done_net_96_amt"]=res["done_sell_96_amt"]-res["done_buy_96_amt"]
            res["done_buy_99_avg"]=res["done_buy_99_amt"]/res["done_buy_99_qty"] if res["done_buy_99_qty"] else None
            res["done_sell_99_avg"]=res["done_sell_99_amt"]/res["done_sell_99_qty"] if res["done_sell_99_qty"] else None
            res2["done_net_99_qty"]=res["done_buy_99_qty"]-res["done_sell_99_qty"]
            res2["done_net_99_amt"]=res["done_sell_99_amt"]-res["done_buy_99_amt"]
            vals[obj.id]=res2
        return vals

    def get_match_profit(self,ids,context={}):
        vals={}
        for obj in self.browse(ids):
            vals[obj.id]=0
        return vals

    def get_margin(self,ids,context={}):
        prices=get_model("gt.price").get_prices()
        vals={}
        for obj in self.browse(ids):
            open_96=obj.conf_net_96_qty+obj.match_net_96_qty
            open_99=obj.conf_net_99_qty+obj.match_net_99_qty
            open_thb=obj.conf_net_96_amt+obj.conf_net_99_amt+obj.match_net_96_amt+obj.match_net_99_amt
            margin_mkt=(obj.fake_deposit or 0)+obj.dep_thb+obj.dep_96_thb+obj.dep_99_thb+max(0,open_thb)+max(0,open_96*prices["cust_96_bid"]+open_99*Decimal(65.6)*prices["cust_99_bid"])
            margin_eq=margin_mkt-max(0,-open_thb)-max(0,-open_96*prices["cust_96_ask"]-open_99*Decimal(65.6)*prices["cust_99_ask"])
            margin=margin_eq*100/margin_mkt if margin_mkt else None
            vals[obj.id]={
                "margin": margin,
                "margin_mkt": margin_mkt,
                "margin_eq": margin_eq,
            }
        return vals

    def get_limit(self, ids, context={}):
        settings=get_model("gt.settings").browse(1)
        prices=get_model("gt.price").get_prices()
        qtys_96=[Decimal(x.strip()) for x in (settings.order_qtys_96 or "").split(",")]
        qtys_99=[Decimal(x.strip()) for x in (settings.order_qtys_99 or "").split(",")]
        vals={}
        for obj in self.browse(ids):
            min_margin=obj.min_margin/Decimal(100)
            lim_buy_96=0
            for qty in qtys_96:
                open_96=obj.conf_net_96_qty+obj.match_net_96_qty+qty
                open_99=obj.conf_net_99_qty+obj.match_net_99_qty
                open_thb=obj.conf_net_96_amt+obj.conf_net_99_amt+obj.match_net_96_amt+obj.match_net_99_amt-qty*prices["cust_96_ask"]
                margin_mkt=(obj.fake_deposit or 0)+obj.dep_thb+obj.dep_96_thb+obj.dep_99_thb+max(0,open_thb)+max(0,open_96*prices["cust_96_bid"]+open_99*Decimal(65.6)*prices["cust_99_bid"])
                margin_eq=margin_mkt-max(0,-open_thb)-max(0,-open_96*prices["cust_96_ask"]-open_99*Decimal(65.6)*prices["cust_99_ask"])
                margin=margin_eq*100/margin_mkt if margin_mkt else None
                if margin is None or (margin<obj.min_margin and margin<(obj.margin or 0)):
                    break
                lim_buy_96=qty
            lim_buy_99=0
            for qty in qtys_99:
                open_96=obj.conf_net_96_qty+obj.match_net_96_qty
                open_99=obj.conf_net_99_qty+obj.match_net_99_qty+qty
                open_thb=obj.conf_net_96_amt+obj.conf_net_99_amt+obj.match_net_96_amt+obj.match_net_99_amt-qty*Decimal(65.6)*prices["cust_99_ask"]
                margin_mkt=(obj.fake_deposit or 0)+obj.dep_thb+obj.dep_96_thb+obj.dep_99_thb+max(0,open_thb)+max(0,open_96*prices["cust_96_bid"]+open_99*Decimal(65.6)*prices["cust_99_bid"])
                margin_eq=margin_mkt-max(0,-open_thb)-max(0,-open_96*prices["cust_96_ask"]-open_99*Decimal(65.6)*prices["cust_99_ask"])
                margin=margin_eq*100/margin_mkt if margin_mkt else None
                print("X"*80)
                print("qty=%s margin=%s"%(qty,margin))
                if margin is None or (margin<obj.min_margin and margin<(obj.margin or 0)):
                    break
                lim_buy_99=qty
            lim_sell_96=0
            for qty in qtys_96:
                open_96=obj.conf_net_96_qty+obj.match_net_96_qty-qty
                open_99=obj.conf_net_99_qty+obj.match_net_99_qty
                open_thb=obj.conf_net_96_amt+obj.conf_net_99_amt+obj.match_net_96_amt+obj.match_net_99_amt+qty*prices["cust_96_bid"]
                margin_mkt=(obj.fake_deposit or 0)+obj.dep_thb+obj.dep_96_thb+obj.dep_99_thb+max(0,open_thb)+max(0,open_96*prices["cust_96_bid"]+open_99*Decimal(65.6)*prices["cust_99_bid"])
                margin_eq=margin_mkt-max(0,-open_thb)-max(0,-open_96*prices["cust_96_ask"]-open_99*Decimal(65.6)*prices["cust_99_ask"])
                margin=margin_eq*100/margin_mkt if margin_mkt else None
                if margin is None or (margin<obj.min_margin and margin<(obj.margin or 0)):
                    break
                lim_sell_96=qty
            lim_sell_99=0
            for qty in qtys_99:
                open_96=obj.conf_net_96_qty+obj.match_net_96_qty
                open_99=obj.conf_net_99_qty+obj.match_net_99_qty-qty
                open_thb=obj.conf_net_96_amt+obj.conf_net_99_amt+obj.match_net_96_amt+obj.match_net_99_amt+qty*Decimal(65.6)*prices["cust_99_bid"]
                margin_mkt=(obj.fake_deposit or 0)+obj.dep_thb+obj.dep_96_thb+obj.dep_99_thb+max(0,open_thb)+max(0,open_96*prices["cust_96_bid"]+open_99*Decimal(65.6)*prices["cust_99_bid"])
                margin_eq=margin_mkt-max(0,-open_thb)-max(0,-open_96*prices["cust_96_ask"]-open_99*Decimal(65.6)*prices["cust_99_ask"])
                margin=margin_eq*100/margin_mkt if margin_mkt else None
                if margin is None or (margin<obj.min_margin and margin<(obj.margin or 0)):
                    break
                lim_sell_99=qty
            vals[obj.id]={
                "lim_buy_96": lim_buy_96,
                "lim_sell_96": lim_sell_96,
                "lim_buy_99": lim_buy_99,
                "lim_sell_99": lim_sell_99,
            }
        return vals

    def get_order_qtys(self, ids, context={}):
        settings=get_model("gt.settings").browse(1)
        qtys_96=[Decimal(x.strip()) for x in (settings.order_qtys_96 or "").split(",")]
        qtys_99=[Decimal(x.strip()) for x in (settings.order_qtys_99 or "").split(",")]
        qtys_96_mini=[Decimal(x.strip()) for x in (settings.order_qtys_96_mini or "").split(",")]
        vals={}
        for obj in self.browse(ids):
            qtys_buy_96=[x for x in qtys_96 if x<=obj.lim_buy_96]
            qtys_sell_96=[x for x in qtys_96 if x<=obj.lim_sell_96]
            qtys_buy_99=[x for x in qtys_99 if x<=obj.lim_buy_99]
            qtys_sell_99=[x for x in qtys_99 if x<=obj.lim_sell_99]
            qtys_buy_96_mini=[x for x in qtys_96_mini if x<=obj.lim_buy_96]
            qtys_sell_96_mini=[x for x in qtys_96_mini if x<=obj.lim_sell_96]
            vals[obj.id]={
                "qtys_buy_96": qtys_buy_96,
                "qtys_sell_96": qtys_sell_96,
                "qtys_buy_99": qtys_buy_99,
                "qtys_sell_99": qtys_sell_99,
                "qtys_buy_96_mini": qtys_buy_96_mini,
                "qtys_sell_96_mini": qtys_sell_96_mini,
            }
        return vals

    def check_account(self,ids,context={}):
        for obj in self.browse(ids):
            if obj.dep_thb<0:
                raise Exception("Insufficient deposit THB balance (%s)"%obj.bal_thb)
            if obj.dep_96<0:
                raise Exception("Insufficient deposit 96.5%% balance (%s)"%obj.bal_96)
            if obj.dep_99<0:
                raise Exception("Insufficient deposit 99.99%% balance (%s)"%obj.bal_99)
            if obj.bal_96<0:
                raise Exception("Insufficient stock 96.5%% balance (%s)"%obj.bal_96)
            if obj.bal_99<0:
                raise Exception("Insufficient stock 99.99%% balance (%s)"%obj.bal_99)
            if not obj.categ_id.disable_margin and obj.margin<obj.min_margin:
                raise Exception("Margin is below minimum (%s < %s)"%(obj.margin,obj.min_margin))

    def signup(self,data,context={}):
        first_name=data.get("first_name")
        if not first_name:
            raise Exception("Missing first name")
        last_name=data.get("last_name")
        if not last_name:
            raise Exception("Missing last name")
        username=data.get("username")
        if not username:
            raise Exception("Missing username")
        username=username.lower()
        password=data.get("password")
        if not password:
            raise Exception("Missing password")
        pin_code=data.get("pin_code")
        email=data.get("email")
        phone=data.get("phone")
        refer_broker=data.get("refer_broker")
        res=get_model("base.user").search([["login","=ilike",username]])
        if res:
            raise Exception("Login is already in use")
        res=get_model("gt.cust.categ").search([["name","=","Normal Customer"]])
        if not res:
            raise Exception("Customer category not found")
        categ_id=res[0]
        vals={
            "name": first_name+" "+last_name,
            "categ_id": categ_id,
            "email": email,
            "phone": phone,
            "refer_broker": refer_broker,
        }
        cust_id=self.create(vals)
        res=get_model("profile").search([["code","=","GT_CUSTOMER"]])
        if not res:
            raise Exception("User profile not found")
        profile_id=res[0]
        vals={
            "login": username,
            "password": password,
            "name": first_name+" "+last_name,
            "profile_id": profile_id,
            "gt_customer_id": cust_id,
            "pin_code": pin_code,
            "email": email,
        }
        user_id=get_model("base.user").create(vals)
        dbname=database.get_active_db()
        token = utils.new_token(dbname, user_id)
        self.trigger([cust_id],"signup")
        return {
            "user_id": user_id,
            "token": token,
            "customer_id": cust_id,
        }

    def login(self,data,context={}):
        username=data.get("username")
        if not username:
            raise Exception("Missing username")
        username=username.lower()
        password=data.get("password")
        if not password:
            raise Exception("Missing password")
        user_id = get_model("base.user").check_password(username, password)
        if not user_id:
            raise Exception("Invalid login")
        user=get_model("base.user").browse(user_id)
        cust_id=user.gt_customer_id.id
        if not cust_id:
            raise Exception("User is not a customer")
        dbname=database.get_active_db()
        token = utils.new_token(dbname, user_id)
        return {
            "user_id": user_id,
            "token": token,
            "customer_id": cust_id,
        }

    def get_customers_per_day(self, context={}):
        db=database.get_connection()
        res=db.query("SELECT date_trunc('day',create_time) AS day,COUNT(*) AS num_cust FROM gt_customer GROUP BY day ORDER BY day")
        n=0
        data=[]
        for r in res:
            d=datetime.strptime(r.day[:10],"%Y-%m-%d")
            n+=r.num_cust
            data.append([time.mktime(d.timetuple()) * 1000, n])
        return data

    def send_reset_password_link(self,login,context={}):
        res=get_model("base.user").search([["login","=ilike",login]])
        if not res:
            raise Exception("Login not found")
        user_id=res[0]
        user=get_model("base.user").browse(user_id)
        email=user.email
        if not email:
            raise Exception("User email not set")
        res=get_model("email.template").search([["name","=","reset_password"]])
        if not res:
            raise Exception("Email template not found")
        tmpl_id=res[0]
        code=str(random.randint(0,999999999))
        user.write({"password_reset_code":code})
        data={
            "email": email,
            "name": user.name,
            "login": user.login,
            "reset_code": code,
        }
        get_model("email.template").create_email([tmpl_id],data)
        get_model("email.message").send_emails_async()
        return {
            "email": email,
        }

    def reset_password(self,login,reset_code,new_password,context={}):
        res=get_model("base.user").search([["login","=ilike",login]])
        if not res:
            raise Exception("Login not found")
        user_id=res[0]
        user=get_model("base.user").browse(user_id)
        if user.password_reset_code!=reset_code:
            raise Exception("Invalid reset code")
        user.write({"password":new_password,"password_reset_code":None})

    def change_password(self,old_password,new_password,context={}):
        user_id=access.get_active_user()
        if not user_id:
            raise Exception("Missing user")
        user=get_model("base.user").browse(user_id)
        if not user.gt_customer_id:
            raise Exception("User is not a customer")
        res=get_model("base.user").check_password(user.login, old_password)
        if not res:
            raise Exception("Invalid old password")
        user.write({"password": new_password})

    def change_pin(self,old_pin,new_pin,context={}):
        # print("change_pin",old_pin,new_pin)
        user_id=access.get_active_user()
        if not user_id:
            raise Exception("Missing user")
        # print("user_id",user_id)
        user=get_model("base.user").browse(user_id)
        if not user.gt_customer_id:
            raise Exception("User is not a customer")
        # print("prev pin_code",user.pin_code)
        if user.pin_code!=old_pin:
            raise Exception("Invalid old PIN")
        user.write({"pin_code": new_pin})

Customer.register()
