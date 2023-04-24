from netforce.model import Model,fields,get_model
from netforce import database
from datetime import *
import time
from dateutil.relativedelta import *
from decimal import *

class Report(Model):
    _name="gt.pl.report"
    _fields={
        "date_from": fields.Date("From Date"),
        "date_to": fields.Date("To Date"),
    }
    _defaults={
        "date_from": lambda *a: date.today().strftime("%Y-%m-01"),
        "date_to": lambda *a: (date.today() + relativedelta(day=31)).strftime("%Y-%m-%d"),
    }

    def get_report_data(self,ids,context={}):
        if ids:
            params = self.read(ids, load_m2o=False)[0]
        else:
            params = self.default_get(load_m2o=False, context=context)
        data={
            "date_from": params["date_from"],
            "date_to": params["date_to"],
        }
        db=database.get_connection()
        res=db.query("SELECT product,type,SUM(qty) AS total_qty,CASE WHEN product='96' THEN SUM(qty*unit_price) WHEN product='99' THEN SUM(qty*unit_price)*65.6 END AS total_amt FROM gt_cust_order WHERE state IN ('confirmed','done') GROUP BY product,type")
        qtys={}
        amts={}
        for r in res:
            qtys[(r.product,r.type)]=r.total_qty
            amts[(r.product,r.type)]=r.total_amt
        data.update({
            "cust_qty_96_buy": qtys.get(("96","buy"),0),
            "cust_qty_96_sell": qtys.get(("96","sell"),0),
            "cust_qty_99_buy": qtys.get(("99","buy"),0),
            "cust_qty_99_sell": qtys.get(("99","sell"),0),
            "cust_amt_96_buy": amts.get(("96","buy"),0),
            "cust_amt_96_sell": amts.get(("96","sell"),0),
            "cust_amt_99_buy": amts.get(("99","buy"),0),
            "cust_amt_99_sell": amts.get(("99","sell"),0),
        })
        data.update({
            "cust_avg_96_buy": data["cust_amt_96_buy"]/data["cust_qty_96_buy"] if data["cust_qty_96_buy"] else None,
            "cust_avg_96_sell": data["cust_amt_96_sell"]/data["cust_qty_96_sell"] if data["cust_qty_96_sell"] else None,
            "cust_avg_99_buy": data["cust_amt_99_buy"]/data["cust_qty_99_buy"]/Decimal(65.6) if data["cust_qty_99_buy"] else None,
            "cust_avg_99_sell": data["cust_amt_99_sell"]/data["cust_qty_99_sell"]/Decimal(65.6) if data["cust_qty_99_sell"] else None,
        })
        data["cust_total_qty_bg"]=data["cust_qty_96_sell"]-data["cust_qty_96_buy"]+data["cust_qty_99_sell"]*Decimal(65.6)-data["cust_qty_99_buy"]*Decimal(65.6)
        data["cust_total_qty_kg"]=data["cust_total_qty_bg"]/Decimal(65.6)
        data["cust_total_amt"]=data["cust_amt_96_buy"]-data["cust_amt_96_sell"]+data["cust_amt_99_buy"]-data["cust_amt_99_sell"]
        data["cust_pl_96"]=(data["cust_avg_96_buy"]-data["cust_avg_96_sell"])*min(data["cust_qty_96_buy"],data["cust_qty_96_sell"]) if data["cust_avg_96_sell"] and data["cust_avg_96_buy"] else 0
        data["cust_pl_99"]=(data["cust_avg_99_buy"]-data["cust_avg_99_sell"])*min(data["cust_qty_99_buy"],data["cust_qty_99_sell"])*Decimal(65.6) if data["cust_avg_99_sell"] and data["cust_avg_99_buy"] else 0
        data["cust_pl"]=data["cust_pl_96"]+data["cust_pl_99"]

        res=db.query("SELECT product,type,SUM(qty) AS total_qty,CASE WHEN product='96' THEN SUM(qty*unit_price) WHEN product='99' THEN SUM(qty*unit_price)*65.6 END AS total_amt FROM gt_sup_order WHERE state IN ('confirmed','done') GROUP BY product,type")
        qtys={}
        amts={}
        for r in res:
            qtys[(r.product,r.type)]=r.total_qty
            amts[(r.product,r.type)]=r.total_amt
        data.update({
            "sup_qty_96_buy": qtys.get(("96","buy"),0),
            "sup_qty_96_sell": qtys.get(("96","sell"),0),
            "sup_qty_99_buy": qtys.get(("99","buy"),0),
            "sup_qty_99_sell": qtys.get(("99","sell"),0),
            "sup_amt_96_buy": amts.get(("96","buy"),0),
            "sup_amt_96_sell": amts.get(("96","sell"),0),
            "sup_amt_99_buy": amts.get(("99","buy"),0),
            "sup_amt_99_sell": amts.get(("99","sell"),0),
        })
        data.update({
            "sup_avg_96_buy": data["sup_amt_96_buy"]/data["sup_qty_96_buy"] if data["sup_qty_96_buy"] else None,
            "sup_avg_96_sell": data["sup_amt_96_sell"]/data["sup_qty_96_sell"] if data["sup_qty_96_sell"] else None,
            "sup_avg_99_buy": data["sup_amt_99_buy"]/data["sup_qty_99_buy"]/Decimal(65.6) if data["sup_qty_99_buy"] else None,
            "sup_avg_99_sell": data["sup_amt_99_sell"]/data["sup_qty_99_sell"]/Decimal(65.6) if data["sup_qty_99_sell"] else None,
        })
        data["sup_total_qty_bg"]=data["sup_qty_96_buy"]-data["sup_qty_96_sell"]+data["sup_qty_99_buy"]*Decimal(65.6)-data["sup_qty_99_sell"]*Decimal(65.6)
        data["sup_total_qty_kg"]=data["sup_total_qty_bg"]/Decimal(65.6)
        data["sup_total_amt"]=data["sup_amt_96_sell"]-data["sup_amt_96_buy"]+data["sup_amt_99_sell"]-data["sup_amt_99_buy"]
        data["sup_pl_96"]=(data["sup_avg_96_sell"]-data["sup_avg_96_buy"])*min(data["sup_qty_96_buy"],data["sup_qty_96_sell"]) if data["sup_avg_96_sell"] and data["sup_avg_96_buy"] else 0
        data["sup_pl_99"]=(data["sup_avg_99_sell"]-data["sup_avg_99_buy"])*min(data["sup_qty_99_buy"],data["sup_qty_99_sell"])*Decimal(65.6) if data["sup_avg_99_sell"] and data["sup_avg_99_buy"] else 0
        data["sup_pl"]=data["sup_pl_96"]+data["sup_pl_99"]

        data.update({
            "all_qty_96_buy": data["cust_qty_96_sell"]+data["sup_qty_96_buy"],
            "all_qty_96_sell": data["cust_qty_96_buy"]+data["sup_qty_96_sell"],
            "all_qty_99_buy": data["cust_qty_99_sell"]+data["sup_qty_99_buy"],
            "all_qty_99_sell": data["cust_qty_99_buy"]+data["sup_qty_99_sell"],
            "all_amt_96_buy": data["cust_amt_96_sell"]+data["sup_amt_96_buy"],
            "all_amt_96_sell": data["cust_amt_96_buy"]+data["sup_amt_96_sell"],
            "all_amt_99_buy": data["cust_amt_99_sell"]+data["sup_amt_99_buy"],
            "all_amt_99_sell": data["cust_amt_99_buy"]+data["sup_amt_99_sell"],
        })
        data.update({
            "all_avg_96_buy": data["all_amt_96_buy"]/data["all_qty_96_buy"] if data["all_qty_96_buy"] else None,
            "all_avg_96_sell": data["all_amt_96_sell"]/data["all_qty_96_sell"] if data["all_qty_96_sell"] else None,
            "all_avg_99_buy": data["all_amt_99_buy"]/data["all_qty_99_buy"]/Decimal(65.6) if data["all_qty_99_buy"] else None,
            "all_avg_99_sell": data["all_amt_99_sell"]/data["all_qty_99_sell"]/Decimal(65.6) if data["all_qty_99_sell"] else None,
        })
        data["all_total_qty_bg"]=data["all_qty_96_buy"]-data["all_qty_96_sell"]+data["all_qty_99_buy"]*Decimal(65.6)-data["all_qty_99_sell"]*Decimal(65.6)
        data["all_total_qty_kg"]=data["all_total_qty_bg"]/Decimal(65.6)
        data["all_total_amt"]=data["all_amt_96_sell"]-data["all_amt_96_buy"]+data["all_amt_99_sell"]-data["all_amt_99_buy"]
        data["all_pl_96"]=(data["all_avg_96_sell"]-data["all_avg_96_buy"])*min(data["all_qty_96_buy"],data["all_qty_96_sell"]) if data["all_avg_96_sell"] and data["all_avg_96_buy"] else 0
        data["all_pl_99"]=(data["all_avg_99_sell"]-data["all_avg_99_buy"])*min(data["all_qty_99_buy"],data["all_qty_99_sell"])*Decimal(65.6) if data["all_avg_99_sell"] and data["all_avg_99_buy"] else 0
        data["all_pl"]=data["all_pl_96"]+data["all_pl_99"]

        return data

Report.register()
