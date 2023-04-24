from netforce.model import Model,fields,get_model 
from netforce import access
from datetime import *
from dateutil.relativedelta import *
import time

def fmt_date(d):
    if not d:
        return None
    return datetime.strptime(d,"%Y-%m-%d").strftime("%d/%m/%Y")

class Report(Model):
    _name="report.gaf.my"
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
                "model": "report.gaf.my",
                "method": "get_file_data",
                "active_id": obj.id,
            },
        }

    def get_file_data(self, ids, context={}):
        print("get_file_data")
        obj=self.browse(ids[0])
        company_id=access.get_active_company() or 1 # XXX
        comp=get_model("company").browse(company_id)
        comp_name=comp.name
        comp_cont=comp.contact_id
        comp_brn=comp_cont.business_no  or "" if comp_cont else None
        comp_gst_no=comp_cont.tax_no or "" if comp_cont else None
        soft_ver="Netforce 4.0"
        gst_ver="2.0"
        d_from=fmt_date(obj.date_from)
        d_to=fmt_date(obj.date_to)
        d_report=time.strftime("%d/%m/%Y")
        data="C|%s|%s|%s|%s|%s|%s|%s|%s\n"%(comp_name,comp_brn,comp_gst_no,d_from,d_to,d_report,soft_ver,gst_ver)
        cond=[["move_id.state","=","posted"], ["move_id.date",">=",obj.date_from],["move_id.date","<=",obj.date_to]]
        cond.append(["tax_comp_id.type","=","vat"])
        purch_count=0
        purch_base_total=0
        purch_tax_total=0
        sale_count=0
        sale_base_total=0
        sale_tax_total=0
        gl_count=0
        gl_debit_total=0
        gl_credit_total=0
        gl_close_bal=0
        p_data=""
        s_data=""
        l_data=""
        for line in get_model("account.move.line").search_browse(cond,order="move_id.date,move_id.number"):
            move=line.move_id
            tax=line.tax_comp_id
            contact=line.contact_id
            if tax.trans_type=="in":
                cont_name=contact.name if contact else None
                cont_brn=contact.business_no if contact else None
                cont_gst_no=contact.tax_no if contact else None
                inv_date=fmt_date(move.date)
                post_date=fmt_date(move.date_posted)
                inv_num=move.number
                import_no="" # XXX
                inv_line_no=1 # XXX
                prod_desc=line.description
                base_amt=line.tax_base
                tax_amt=line.debit-line.credit
                tax_code=tax.tax_rate_id.code # XXX
                currency_code=line.currency_id.code if line.currency_id else None
                amount_cur=line.amount_cur
                tax_cur=None # XXX
                p_data+="P|%s|%s|%s|%s|%s|%s|%s|%s|%s|%s|%s|%s|%s|%s|%s\n"%(cont_name,cont_brn,cont_gst_no,inv_date,post_date,inv_num,import_no,inv_line_no,prod_desc,base_amt,tax_amt,tax_code,currency_code,amount_cur,tax_cur)
                purch_count+=1
                purch_base_total+=base_amt
                purch_tax_total+=tax_amt
            elif tax.trans_type=="out":
                cont_name=contact.name if contact else None
                cont_brn=contact.business_no if contact else None
                cont_gst_no=contact.tax_no if contact else None
                inv_date=fmt_date(move.date)
                post_date=fmt_date(move.date_posted)
                inv_num=move.number
                import_no="" # XXX
                inv_line_no=1 # XXX
                prod_desc=line.description
                base_amt=line.tax_base
                tax_amt=line.credit-line.debit
                tax_code=tax.tax_rate_id.code # XXX
                currency_code=line.currency_id.code if line.currency_id else None
                amount_cur=line.amount_cur
                tax_cur=None # XXX
                s_data+="S|%s|%s|%s|%s|%s|%s|%s|%s|%s|%s|%s|%s|%s|%s|%s\n"%(cont_name,cont_brn,cont_gst_no,inv_date,post_date,inv_num,import_no,inv_line_no,prod_desc,base_amt,tax_amt,tax_code,currency_code,amount_cur,tax_cur)
                sale_count+=1
                sale_base_total+=base_amt
                sale_tax_total+=tax_amt
            trans_date=fmt_date(move.date)
            acc_code=line.account_id.code
            if line.account_id.type in ["revenue", "cost_sales", "other_income", "expense", "other_expense"]:
                acc_type="PL"
            else:
                acc_type="BS"
            acc_name=line.account_id.name
            trans_desc=line.description
            cont_name=contact.name if contact else ""
            trans_id=move.number
            src_doc=move.ref or ""
            src_type=""
            debit=line.debit or 0
            credit=line.credit or 0
            gl_close_bal+=debit-credit # XXX
            l_data+="L|%s|%s|%s|%s|%s|%s|%s|%s|%s|%s|%s|%s\n"%(trans_date,acc_code,acc_type,acc_name,trans_desc,cont_name,trans_id,src_doc,src_type,debit,credit,gl_close_bal)
            gl_count+=1
            gl_debit_total+=debit
            gl_credit_total+=credit
        data+=p_data
        data+=s_data
        data+=l_data
        data+="F|%s|%s|%s|%s|%s|%s|%s|%s|%s|%s"%(purch_count,purch_base_total,purch_tax_total,sale_count,sale_base_total,sale_tax_total,gl_count,gl_debit_total,gl_credit_total,gl_close_bal)
        return {
            "filename": "GAF-%s.txt"%obj.date_to,
            "content_type": "text/plain",
            "data": data,
        }

Report.register()
