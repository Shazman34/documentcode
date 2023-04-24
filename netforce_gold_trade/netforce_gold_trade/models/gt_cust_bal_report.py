from netforce.model import Model,fields,get_model
from netforce import database
from datetime import *
import time

class Report(Model):
    _name="gt.cust.bal.report"
    _fields={
        "customer_id": fields.Many2One("gt.customer","Customer",required=True),
        "date": fields.Date("Date",required=True),
    }
    _defaults={
        "date": lambda *a: time.strftime("%Y-%m-%d %H:%M:%S"),
    }

    def get_report_data(self,ids,context={}):
        if not ids:
            return {"lines":[]}
        obj=self.browse(ids[0])
        cust=obj.customer_id
        data={
            "cust_name": cust.name,
            "date": obj.date,
        }
        lines=[]
        for pmt in cust.payments:
            if pmt.state!="done":
                continue
            vals={
                "ref": pmt.number,
                "link_url": "/action?name=gt_cust_payment&mode=form&active_id=%d"%pmt.id,
                "time": pmt.create_time,
            }
            if pmt.direction=="in":
                vals["amt"]=pmt.amount_total
            elif pmt.direction=="out":
                vals["amt"]=-pmt.amount_total
            lines.append(vals)
        for deliv in cust.deliveries:
            if deliv.state!="done":
                continue
            vals={
                "ref": deliv.number,
                "link_url": "/action?name=gt_cust_delivery&mode=form&active_id=%d"%deliv.id,
                "time": deliv.create_time,
            }
            if deliv.direction=="in":
                for line in deliv.lines:
                    if line.product=="96":
                        vals["qty_96"]=line.qty
                    elif line.product=="99":
                        vals["qty_99"]=line.qty
            elif deliv.direction=="out":
                for line in deliv.lines:
                    if line.product=="96":
                        vals["qty_96"]=-line.qty
                    elif line.product=="99":
                        vals["qty_99"]=-line.qty
            lines.append(vals)
        for order in cust.orders:
            if order.state!="done":
                continue
            vals={
                "ref": order.number,
                "link_url": "/action?name=gt_cust_order&mode=form&active_id=%d"%order.id,
                "time": order.create_time,
            }
            if order.type=="buy":
                vals["amt"]=-order.amount-(order.late_fee or 0)
                if order.product=="96":
                    vals["qty_96"]=order.qty
                elif order.product=="99":
                    vals["qty_99"]=order.qty
            elif order.type=="sell":
                vals["amt"]=order.amount-(order.late_fee or 0)
                if order.product=="96":
                    vals["qty_96"]=-order.qty
                elif order.product=="99":
                    vals["qty_99"]=-order.qty
            lines.append(vals)
        lines.sort(key=lambda l: l["time"])
        bal_amt=0
        bal_qty_96=0
        bal_qty_99=0
        for line in lines:
            bal_amt+=line.get("amt",0)
            bal_qty_96+=line.get("qty_96",0)
            bal_qty_99+=line.get("qty_99",0)
            line["bal_amt"]=bal_amt
            line["bal_qty_96"]=bal_qty_96
            line["bal_qty_99"]=bal_qty_99
        lines.sort(key=lambda l: l["time"],reverse=True)
        data["lines"]=lines
        return data

Report.register()
