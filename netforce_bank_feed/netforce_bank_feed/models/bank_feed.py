from netforce.model import Model,fields,get_model
import requests
from lxml import html
import json
import os
from datetime import *
from dateutil.relativedelta import *
from netforce import utils
from decimal import *
from pprint import pprint

class BankFeed(Model):
    _name="bank.feed"
    _string="Bank Feed"
    _name_field="account_no"
    _fields={
        "type": fields.Selection([["ksme","KCyber SME"],["kbiz","KBizNet"],["maybank","Maybank"],["cimb","CIMB"],["ocbc","OCBC"]],"Type",required=True),
        "account_id": fields.Many2One("account.account","Account",required=True),
        "username": fields.Char("Username",required=True),
        "password": fields.Char("Password"),
        "company": fields.Char("Company"),
        "account_no": fields.Char("Account Number",required=True),
        "state": fields.Selection([["active","Active"],["inactive","Inactive"]],"Status",required=True),
    }
    _defaults={
        "state": "active",
    }

    def import_all(self,context={}):
        for obj in self.search_browse([["state","=","active"]]):
            obj.import_statements()
            obj.account_id.auto_bank_reconcile()
            obj.account_id.reconcile_all_matched()
        self.update_sale_orders()

    def update_sale_orders(self):
        print("Updating sales orders...")
        d_from=(datetime.today()-timedelta(days=10)).strftime("%Y-%m-%d")
        sale_ids=get_model("sale.order").search([["date",">=",d_from]])
        get_model("sale.order").function_store(sale_ids)

    def import_statements(self,ids,context={}):
        obj=self.browse(ids[0])
        script_dir=os.path.dirname(os.path.abspath(__file__))+"/../scripts"
        print("script_dir",script_dir)
        data={
            "feed_type": obj.type,
            "company": obj.company,
            "username": obj.username,
            "password": obj.password,
            "account": obj.account_no,
        }
        print("POST data",data)
        req=requests.post("https://api.xbank.com/get_transactions",json=data)
        if req.status_code!=200:
            raise Exception("Invalid status code: %s (%s)"%(req.status_code,req.text))
        data=req.json()
        transactions=data.get("transactions")
        if transactions is not None:
            print("got transactions",data)
            for line in transactions:
                line["received"]=Decimal(line["received"] or 0)
                line["spent"]=Decimal(line["spent"] or 0)
                line["balance"]=Decimal(line["balance"] or 0)
            obj.import_statement_data(transactions)
            return {
                "flash": "Transactions imported successfully",
            }
        proc_id=data.get("proc_id")
        if not proc_id:
            raise Exception("Invalid response: missing proc_id")
        return {
            "next": {
                "name": "bank_feed_enter_token",
                "context": {
                    "proc_id": proc_id,
                    "feed_id": obj.id,
                },
            }
        }

    def import_continue(self,ids,proc_id,token,context={}):
        obj=self.browse(ids[0])
        data={
            "proc_id": proc_id,
            "token": token,
        }
        req=requests.post("https://api.xbank.com/continue",json=data)
        if req.status_code!=200:
            raise Exception("Invalid status code: %s (%s)"%(req.status_code,req.text))
        data=req.json()
        transactions=data.get("transactions")
        if not transactions:
            raise Exception("Invalid response: missing transactions")
        print("got transactions",data)
        for line in transactions:
            line["received"]=Decimal(line["received"] or 0)
            line["spent"]=Decimal(line["spent"] or 0)
            line["balance"]=Decimal(line["balance"] or 0)
        obj.import_statement_data(transactions)
        return {
            "flash": "Transactions imported successfully",
        }

    def import_statement_data(self,ids,data,context={}):
        print("BankFeed.import_statement_data")
        obj=self.browse(ids[0])
        month_data={}
        for line in data:
            month=line["date"][:7]
            month_data.setdefault(month,[])
            month_data[month].append(line)
        for month,lines in month_data.items(): 
            obj.import_statement_data_month(month,lines)

    def import_statement_data_month(self,ids,month,lines,context={}):
        print("BankFeed.import_statement_data_month",month)
        obj=self.browse(ids[0])
        rev_lines=list(reversed(lines)) # from oldest to newwest
        #rev_lines=lines # XXX
        date_start=month+"-01"
        date_end=(datetime.strptime(date_start,"%Y-%m-%d")+relativedelta(day=31)).strftime("%Y-%m-%d")
        start_line_no=None
        res=get_model("account.statement").search([["account_id","=",obj.account_id.id],["date_start","=",date_start]])
        if res:
            st_id=res[0]
            print("found statement st_id=%s"%st_id)
            st=get_model("account.statement").browse(st_id)
            last=st.lines[-1]
            for i,line in enumerate(rev_lines):
                if line["date"]!=last.date:
                    continue
                if line["description"]!=last.description:
                    continue
                if line["received"]!=last.received:
                    continue
                if line["spent"]!=last.spent:
                    continue
                #if line["balance"]!=last.balance:
                #    continue
                start_line_no=i+1
                break
            if start_line_no is None:
                pprint(lines)
                raise Exception("Last imported statement line not found in new data: %s %s %s %s %s %s"%(obj.account_id.name,last.date,last.description,last.received,last.spent,last.balance))
        if start_line_no is None:
            print("new statement")
            first=rev_lines[0]
            bal_start=first["balance"]-first["received"]+first["spent"]
            vals={
                "account_id": obj.account_id.id,
                "date_start": date_start,
                "date_end": date_end,
                "balance_start": bal_start,
            }
            print("create statement",vals)
            st_id=get_model("account.statement").create(vals)
            start_line_no=0
        print("start_line_no=%s"%start_line_no)
        for line in rev_lines[start_line_no:]:
            vals={
                "statement_id": st_id,
                "date": line["date"],
                "description": line["description"],
                "received": line["received"],
                "spent": line["spent"],
                "balance": line["balance"],
            }
            print("create statement line",vals)
            line_id=get_model("account.statement.line").create(vals)

BankFeed.register()
