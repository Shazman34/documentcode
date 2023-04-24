import time
from netforce.model import Model, fields, get_model
from . import utils
from netforce.access import get_active_company

class Report(Model):
    _name="report.pnd1.kor"
    _transient=True
    _fields={
        "year": fields.Date("Year"),
    }
    _defaults={
        "year": lambda *a: time.strftime("%Y-%m-%d"),
    }

    def print_cover(self,ids,context={}):
        obj=self.browse(ids)[0]
        return {
            "next": {
                "name": "report_pnd1_kor_cover_pdf",
                "year": obj.year,
            }
        }

    def print_attach(self,ids,context={}):
        obj=self.browse(ids)[0]
        return {
            "next": {
                "name": "report_pnd1_kor_attach_pdf",
                "year": obj.year,
            }
        }

    def get_data(self,context={}):
        company_id=get_active_company()
        comp=get_model("company").browse(company_id)
        year=context.get("year")
        if not year:
            year=time.strftime("%Y-%m-%d")
        year=year[0:4]
        date_from=year+"-01-01"
        date_to=year+"-12-31"
        lines=[]
        employee=get_model('hr.employee')
        date2thai=utils.date2thai
        for emp in employee.search_browse([],order='id'):
            emp_name=' '.join(s for s in [(emp.title and emp.title+'.' or ''),(emp.first_name or ''),(emp.last_name or '')])
            line={
                'line_base':0.0,
                'line_tax':0.0,
                'line_address': employee.get_address([emp.id]), 
                'line_cond': '1',
                'line_name': emp_name,
                'line_pin': emp.tax_no,
                'line_wht_item': '01',
                }
            for slip in get_model("hr.payslip").search_browse([['employee_id','=',emp.id],["date",">=",date_from],["date","<=",date_to], ["state","=","approved"]]):
                line["line_base"]+=slip.amount_wage+slip.amount_allow
                line["line_tax"]+=slip.amount_tax
            # only who have income
            if line['line_base'] > 0:
                lines.append(line)
        settings=get_model("settings").browse(1)
        document_date=date2thai(time.strftime("%Y-%m-%d"),'%(d)s,%(Tm)s,%(BY)s').split(',')
        data={
            "pin": settings.tax_no,
            "company": comp.name,
            "year": document_date[2],
            "document_date": document_date,
            'norecord': False,
            "lines": lines,
        }
        return data

Report.register()
