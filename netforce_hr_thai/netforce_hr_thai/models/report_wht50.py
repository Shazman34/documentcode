import time
from netforce.model import Model, fields, get_model
from . import utils
from netforce.access import get_active_company

class Report(Model):
    _name="report.wht50"
    _transient=True
    _fields={
        "year": fields.Date("Year"),
        "employee_id": fields.Many2One("hr.employee","Employee"),
    }
    _defaults={
        "year": lambda *a: time.strftime("%Y-%m-%d"),
    }

    def print_wht50(self,ids,context={}):
        obj=self.browse(ids)[0]
        employee_id=obj.employee_id and obj.employee_id.id or None
        return {
            "next": {
                "name": "report_wht50_pdf",
                "year": obj.year,
                "employee_id": employee_id,
            }
        }

    def get_data(self,context={}):
        company_id=get_active_company()
        comp=get_model("company").browse(company_id)
        year=context.get("year")
        employee_id=context.get("employee_id")
        if not year:
            year=time.strftime("%Y-%m-%d")
        year=year[0:4]
        date_from=year+"-01-01"
        date_to=year+"-12-31"
        lines=[]
        emp_obj=None
        employee=get_model('hr.employee')
        if employee_id != 'null':
            emp_obj=employee.search_browse([['id','=',employee_id]])
        else:
            emp_obj=employee.search_browse([],order='id')

        # get current date
        document_date=utils.date2thai(time.strftime("%Y-%m-%d"),'%(d)s,%(Tm)s,%(BY)s').split(',')
        for emp in emp_obj:
            emp_name=' '.join(s for s in [(emp.title and emp.title+'.' or ''),(emp.first_name or ''),(emp.last_name or '')])
            line={
                'line_name': emp_name,
                'line_address': employee.get_address([emp.id]), 
                'line_pin': emp.tax_no,
                'line_base': 0.0,
                'line_tax': 0.0,
                'line_base_sum': 0.0,
                'line_tax_sum': 0.0,
                'line_sso_sum': 0.0,
                'line_prov_sum': 0.0,
                'line_tax_sum_word': '',
                'line_year': document_date[2],
                }
            for slip in get_model("hr.payslip").search_browse([['employee_id','=',emp.id],["date",">=",date_from],["date","<=",date_to], ["state","=","approved"]]):
                line["line_base"]+=slip.amount_wage+slip.amount_allow-slip.amount_deduct
                line["line_tax"]+=slip.amount_tax
                line["line_sso_sum"]+=slip.amount_social
                line["line_prov_sum"]+=slip.amount_provident

            line['line_base_sum']=line['line_base']
            line['line_tax_sum']=line['line_tax']
            line['line_tax_sum_word']=utils.num2word(line['line_tax_sum'])
            # only who have income
            if line['line_base'] > 0:
                lines.append(line)

        settings=get_model("settings").browse(1)

        data={
            "company_pin": settings.tax_no,
            "company_name": comp.name,
            "company_address": settings.get_address_str() or '',
            "year": document_date[2],
            "document_date": document_date,
            'norecord': False if lines else True,
            "lines": lines,
        }

        return data

Report.register()
