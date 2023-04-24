from netforce.model import Model,fields,get_model
from netforce import database
from datetime import *
from pprint import pprint

class Report(Model):
    _name="nd.report.return"
    _fields={
        "date_from": fields.Date("From Date"),
        "date_to": fields.Date("To Date"),
    }

    def get_report_data(self,ids,context={}):
        print("get_report_data",ids)
        db=database.get_connection()
        res=db.query("SELECT o.customer_id,l.product_id,SUM(l.qty) AS total_qty FROM nd_order_line l JOIN nd_order o ON o.id=l.order_id WHERE o.state='done' GROUP BY o.customer_id,l.product_id")
        num_out={}
        cust_ids=[]
        prod_ids=[]
        for r in res:
            k=(r.customer_id,r.product_id)
            num_out.setdefault(k,0)
            num_out[k]+=r.total_qty
            cust_ids.append(r.customer_id)
            prod_ids.append(r.product_id)
        customers=[]
        for cust in get_model("contact").browse(cust_ids):
            prods=[]
            for prod in get_model("product").browse(prod_ids):
                k=(cust.id,prod.id)
                out_qty=num_out.get(k,0)
                in_qty=0
                bal_qty=out_qty-in_qty
                if bal_qty!=0:
                    prod_vals={
                        "name": prod.name,
                        "out_qty": out_qty,
                        "in_qty": 0,
                        "bal_qty": bal_qty,
                    }
                    prods.append(prod_vals)
            if not prods:
                continue
            prods.sort(key=lambda x: x["name"])
            cust_vals={
                "id": cust.id,
                "code": cust.code,
                "first_name": cust.first_name,
                "last_name": cust.last_name,
                "products": prods,
            }
            customers.append(cust_vals)
        customers.sort(key=lambda x: x["code"])
        data={
            "customers": customers,
        }
        pprint(data)
        return data

Report.register()
