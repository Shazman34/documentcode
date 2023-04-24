import time
from netforce.model import Model, fields, get_model
from . import utils
from netforce.access import get_active_company

class Report(Model):
    _name="report.sso"
    _transient=True
    _fields={
        "month": fields.Date("Month"),
        "option": fields.Selection([["01","Detail of sending to the contribution"],["02","Disk"],["03","Internet"],["04","Others"]],"Cover Sending"),
    }
    _defaults={
        "month": lambda *a: time.strftime("%Y-%m-%d"),
        "option": "01",
    }

    def get_payslip_line(self,month):
        if not month:
            month=time.strftime("%Y-%m-%d")
        last_date=utils.get_last_day(month)
        date_from=month[0:8]+"01"
        date_to=month[0:8]+str(last_date)
        payslip_line=get_model("hr.payslip").search_browse([["date",">=",date_from],["date","<=",date_to], ["state","=","approved"]])

        if len(payslip_line) < 1:
            raise Exception("No data available")

        return payslip_line

    def print_cover(self,ids,context={}):
        obj=self.browse(ids)[0]
        payslip_line=self.get_payslip_line(obj.month)
        return {
            "next": {
                "name": "report_sso_cover_pdf",
                "month": obj.month,
                "option": obj.option,
            }
        }

    def print_attach(self,ids,context={}):
        obj=self.browse(ids)[0]
        payslip_line=self.get_payslip_line(obj.month)
        return {
            "next": {
                "name": "report_sso_attach_pdf",
                "month": obj.month,
                "option": obj.option,
            }
        }

    def get_data(self,context={}):
        company_id=get_active_company()
        comp=get_model("company").browse(company_id)
        month=context.get("month")
        option=context.get("option")
        lines=[]
        for slip in self.get_payslip_line(month):
            emp=slip.employee_id
            emp_name=' '.join(s for s in [(emp.title and emp.title+'.' or ''),(emp.first_name or ''),(emp.last_name or '')])
            line={
                "line_base": slip.amount_wage,
                'line_deduction': slip.amount_social,
                'line_name': emp_name,
                'line_pin': emp.tax_no,
            }
            lines.append(line)


        settings=get_model("settings").browse(1)
        address=settings.get_address_str() or ''
        company_address=''
        company_zip=''
        if address:
            company_address=address
            company_zip=settings.addresses[0].postal_code

        setting=get_model('hr.payroll.settings').browse(1)
        if setting:
            company_sso=setting.social_number
            company_sso_perc=setting.social_rate

        document_date=dict(zip(['d','m','y'],utils.date2thai(time.strftime("%Y-%m-%d"),'%(d)s,%(Tm)s,%(BY)s').split(',')))
        period_month=document_date['m']
        period_year=document_date['y']
        document_date=[document_date['d'],document_date['m'],document_date['y']]

        sum_base=0.0
        sum_deduction=0.0
        sum_comp_contrib=0.0
        for line in lines:
            sum_base+=line['line_base'] 
            sum_deduction+=line['line_deduction'] 
            sum_comp_contrib+=line['line_deduction'] 
        
        sum_total=sum_deduction+sum_comp_contrib
        data={
            'period_month': period_month,
            'period_year': period_year,
            'company_address': company_address,
            'company_fax': settings.fax,
            'company_name': comp.name,
            'company_phone': settings.phone,
            'company_sso': company_sso,
            'company_sso_perc': company_sso_perc,
            'company_zip': company_zip,
            'document_date': document_date,
            'norecord': False if lines else True,
            'sum_base': sum_base,
            'sum_deduction': sum_deduction,
            'sum_comp_contrib': sum_comp_contrib,
            'sum_total': sum_total,
            'sum_total_word': utils.num2word(sum_total),
            'send_to': option,
            "lines": lines,
        }
        return data

Report.register()
