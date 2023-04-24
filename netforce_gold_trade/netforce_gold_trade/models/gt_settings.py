from netforce.model import Model,fields,get_model
from netforce import database
import requests
import json
from datetime import *
import time

class Settings(Model):
    _name="gt.settings"
    _string="Settings"
    _name_field="market_state"
    _audit_log=True
    _fields={
        "market_state": fields.Selection([["open","Open"],["closed","Closed"]],"Market Status",function="get_market_state",function_multi=True),
        "market_open_time": fields.Char("Market Open Time"),
        "market_close_time": fields.Char("Market Close Time"),
        "market_state_manual": fields.Selection([["open","Open"],["closed","Closed"]],"Market Manual Status"),
        "pending_cancel_time": fields.Char("Pending Cancel Time"),
        "manual_usd_thb": fields.Decimal("Manual USD/THB"),
        "manual_cust_99_bid": fields.Decimal("Manual G99 Bid (THB/baht)"),
        "manual_cust_99_ask": fields.Decimal("Manual G99 Ask (THB/baht)"),
        "manual_cust_96_bid": fields.Decimal("Manual G96 Bid (THB/baht)"),
        "manual_cust_96_ask": fields.Decimal("Manual G96 Ask (THB/baht)"),
        "cust_99_premium": fields.Decimal("G99 Premium"),
        "cust_99_spread": fields.Decimal("G99 Spread"),
        "cust_96_premium": fields.Decimal("G96 Premium"),
        "cust_96_spread": fields.Decimal("G96 Spread"),
        "seq_cust_id": fields.Many2One("sequence","Customer Sequence"),
        "seq_cust_order_id": fields.Many2One("sequence","Customer Order Sequence"),
        "seq_cust_match_id": fields.Many2One("sequence","Customer Match Sequence"),
        "seq_cust_payment_id": fields.Many2One("sequence","Customer Payment Sequence"),
        "seq_cust_delivery_id": fields.Many2One("sequence","Customer Delivery Sequence"),
        "seq_cust_deposit_id": fields.Many2One("sequence","Customer Deposit Sequence"),
        "seq_sup_order_id": fields.Many2One("sequence","Supplier Order Sequence"),
        "min_margin": fields.Decimal("Default Min Margin (%)"), # XXX: deprecated
        "order_qtys_96": fields.Text("Allowed Order Qtys (96.5%)"),
        "order_qtys_99": fields.Text("Allowed Order Qtys (99.99%)"),
        "order_qtys_96_mini": fields.Text("Allowed Order Qtys (96.5% MINI)"),
        "late_pay_fee": fields.Decimal("Late Payment Fee (THB/baht/day)"),
        "bank_accounts": fields.One2Many("bank.account","related_id","Bank Accounts"),
        "market_open_time_96_mini": fields.Char("Market Open Time (96.5% Mini)"),
        "market_close_time_96_mini": fields.Char("Market Close Time (96.5% Mini)"),
        "market_state_96_mini": fields.Selection([["open","Open"],["closed","Closed"]],"Market Status 96.5% MINI",function="get_market_state",function_multi=True),
        "market_state_manual_96_mini": fields.Selection([["open","Open"],["closed","Closed"]],"Market Manual Status 96.5% MINI"),
    }

    def get_market_state(self,ids,context={}):
        t=time.strftime("%H:%M")
        d=datetime.today()
        vals={}
        for obj in self.browse(ids):
            state="open"
            if d.weekday() in (5,6):
                state="closed"
            if obj.market_open_time and t<obj.market_open_time:
                state="closed"
            if obj.market_close_time and t>=obj.market_close_time:
                state="closed"
            if obj.market_state_manual:
                state=obj.market_state_manual
            state_96="open"
            if d.weekday() in (5,6):
                state_96="closed"
            if obj.market_open_time_96_mini and t<obj.market_open_time_96_mini:
                state_96="closed"
            if obj.market_close_time_96_mini and t>=obj.market_close_time_96_mini:
                state_96="closed"
            if obj.market_state_manual_96_mini:
                state_96=obj.market_state_manual_96_mini
            vals[obj.id]={
                "market_state": state,
                "market_state_96_mini": state_96,
            }
        return vals

Settings.register()
