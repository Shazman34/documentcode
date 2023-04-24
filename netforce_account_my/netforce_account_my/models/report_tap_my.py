from netforce.model import Model,fields,get_model 
from netforce import access
from datetime import *
from dateutil.relativedelta import *
import time

class Report(Model):
    _name="report.tap.my"
    _transient=True
    _fields={
        "date_from": fields.Date("From Date",required=True),
        "date_to": fields.Date("To Date",required=True),
    }

    def default_get(self, field_names=None, context={}, **kw):
        defaults = context.get("defaults", {})
        date_from = defaults.get("date_from")
        if not date_from:
            date_from = date.today().strftime("%Y-%m-01")
        date_to = defaults.get("date_to")
        if not date_to:
            date_to = (date.today() + relativedelta(day=31)).strftime("%Y-%m-%d")
        return {
            "date_from": date_from,
            "date_to": date_to,
        }

    def download_file(self, ids, context={}):
        print("download_file")
        obj=self.browse(ids[0])
        return {
            "next": {
                "type": "download",
                "model": "report.tap.my",
                "method": "get_file_data",
                "active_id": obj.id,
            },
        }

    def get_file_data(self, ids, context={}):
        print("get_file_data")
        obj=self.browse(ids[0])
        company_id=access.get_active_company() or 1 # XXX
        comp=get_model("company").browse(company_id)
        cond=[["move_id.state","=","posted"], ["move_id.date",">=",obj.date_from],["move_id.date","<=",obj.date_to]]
        cond.append(["tax_comp_id.type","=","vat"])
        in_base=0
        in_tax=0
        in_totals={}
        out_base=0
        out_tax=0
        out_totals={}
        for line in get_model("account.move.line").search_browse(cond,order="move_id.date,move_id.number"):
            move=line.move_id
            tax=line.tax_comp_id
            code=tax.code
            if tax.trans_type=="in":
                base_amt=line.tax_base
                tax_amt=line.debit-line.credit
                in_base+=base_amt
                in_tax+=tax_amt
                in_totals.setdefault(code,0)
                in_totals[code]+=tax_amt
            elif tax.trans_type=="out":
                base_amt=line.tax_base
                tax_amt=line.credit-line.debit
                out_base+=base_amt
                out_tax+=tax_amt
                out_totals.setdefault(code,0)
                out_totals[code]+=tax_amt
        carry_forward=0 # XXX
        out_local=0
        out_export=0
        out_exempt=0
        out_relief=0
        ats_import=0
        capital_goods=0
        bad_debt_relief=0
        bad_debt_recover=0
        msic1=""
        msic1_val=""
        msic2=""
        msic2_val=""
        msic3=""
        msic3_val=""
        msic4=""
        msic4_val=""
        msic5=""
        msic5_val=""
        out_details=sorted([(amt,code) for (code,amt) in out_totals.items()])
        if len(out_details)>0:
            msic1=out_details[0][1]
            msic1_val=out_details[0][0]
        if len(out_details)>1:
            msic2=out_details[1][1]
            msic2_val=out_details[1][0]
        if len(out_details)>2:
            msic3=out_details[2][1]
            msic3_val=out_details[2][0]
        if len(out_details)>3:
            msic4=out_details[3][1]
            msic4_val=out_details[3][0]
        if len(out_details)>4:
            msic5=out_details[4][1]
            msic5_val=out_details[4][0]
        other_val=0
        for code,amt in out_details[5:]:
            other_val+=amt
        data="%s|%s|%s|%s|%s|%s|%s|%s|%s|%s|%s|%s|%s|%s|%s|%s|%s|%s|%s|%s|%s|%s|%s|%s"%(out_base,out_tax,in_base,in_tax,carry_forward,out_local,out_export,out_exempt,out_relief,ats_import,capital_goods,bad_debt_relief,bad_debt_recover,msic1,msic1_val,msic2,msic2_val,msic3,msic3_val,msic4,msic4_val,msic5,msic5_val,other_val)
        return {
            "filename": "TAP-%s.txt"%obj.date_to,
            "content_type": "text/plain",
            "data": data,
        }

Report.register()
