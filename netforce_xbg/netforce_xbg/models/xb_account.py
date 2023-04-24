from netforce.model import Model,fields,get_model
from netforce import access
from netforce import utils
from netforce import database
from datetime import *
import time
import requests
import json
import random
import hashlib
from netforce.logger import audit_log


class Account(Model):
    _name="xb.account"
    _string="Account"
    _name_field="email"
    _fields={
        "date_created": fields.DateTime("Date Created",required=True),
        "email": fields.Char("Email",required=True),
        "orders": fields.One2Many("xb.order","account_id","Orders"),
        "gold_balance": fields.Decimal("Gold Balance",function="get_gold_balance",scale=9),
        "user_id": fields.Many2One("base.user","User"),
    }

    _defaults={
        "date_created": lambda *a: time.strftime("%Y-%m-%d %H:%M:%S"),
    }
    _order="date_created"

    def get_gold_balance(self,ids,context={}):
        vals={}
        for obj in self.browse(ids):
            bal=0
            for order in obj.orders:
                if order.state=="done":
                    if order.side=="buy":
                        bal+=order.qty
                    elif order.side=="sell":
                        bal-=order.qty
            vals[obj.id]=bal
        return vals

    def signup(self,email,password,context={}):
        access.set_active_user(1)
        if not utils.check_email_syntax(email):
            raise Exception("Invalid email")
        email=email.lower()
        res = self.search([["email","=",email]])
        if res:
            raise Exception("Email is already registered")
        res=get_model("profile").search([["code","=","XB_ACCOUNT"]]) # XXX
        if not res:
            raise Exception("Profile not found")
        profile_id=res[0]
        vals={
            "name": "N/A",
            "login": email,
            "email": email,
            "password": password,
            "profile_id": profile_id,
        }
        user_id=get_model("base.user").create(vals)
        vals={
            "email": email,
            "user_id": user_id,
        }
        acc_id=get_model("xb.account").create(vals)
        dbname=database.get_active_db()
        token=utils.new_token(dbname,user_id)
        return {
            "user_id": user_id,
            "token": token,
        }

    def login(self,email,password,context={}):
        access.set_active_user(None)
        user_id = get_model("base.user").check_password(email, password)
        if not user_id:
            audit_log("Invalid login (%s)" % email)
            db = database.get_connection()
            db.commit()
            raise Exception("Invalid login")
        try:
            access.set_active_user(1)
            user = get_model("base.user").browse(user_id)
            t = time.strftime("%Y-%m-%d %H:%M:%S")
            user.write({"lastlog": t})
            dbname=database.get_active_db()
            token = utils.new_token(dbname, user_id)
            return {
                "user_id": user_id,
                "token": token,
            }
        finally:
            access.set_active_user(user_id)
            audit_log("Login (%s)" % email)

Account.register()
