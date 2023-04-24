import time
from netforce.model import Model, fields, get_model
from . import utils
from netforce.access import get_active_company

class Report(Model):
    _name="report.provident"
    _transient=True
    _fields={
        "month": fields.Date("Month"),
    }
    _defaults={
        "month": lambda *a: time.strftime("%Y-%m-%d"),
    }

    def get_payslip_line(self,month):
        if not month:
            month=time.strftime("%Y-%m-%d")
        last_day=utils.get_last_day(month)
        date_from=month[0:8]+"01"
        date_to=month[0:8]+str(last_day)
        payslip_line=get_model("hr.payslip").search_browse([["date",">=",date_from],["date","<=",date_to], ["state","=","approved"]])
        has_prov=0
        for slip in payslip_line:
            if slip.amount_provident > 0:
                has_prov+=1

        if len(payslip_line) < 1 or has_prov < 1:
            raise Exception("No data available")

        return payslip_line

    def print_provident(self,ids,context={}):
        obj=self.browse(ids)[0]
        payslip_line=self.get_payslip_line(obj.month)

        return {
            "next": {
                "name": "report_provident_pdf",
                "month": obj.month,
            }
        }

    def get_data(self,context={}):
        company_id=get_active_company()
        comp=get_model("company").browse(company_id)
        month=context.get("month")
        lines=[]
        no=1
        for slip in self.get_payslip_line(month):
            if slip.amount_provident < 1:
                continue
            emp=slip.employee_id
            emp_name=' '.join(s for s in [(emp.title and emp.title+'.' or ''),(emp.first_name or ''),(emp.last_name or '')])

            line={
                'no': no,
                'tran_code': '',
                'employee_code': emp.code,
                'prov_code': emp.prov_fund_no,
                'employee_name': emp_name,
                'id_code': emp.id_no,
                'tax_id': emp.tax_no,
                'date_cal_year': '',
                'start_work_date': emp.hire_date and emp.hire_date.replace("-","/") or '',
                'open_ac_date': emp.prov_open_date,
                'salary': emp.salary,
                'num_of_restdays': 0,
                'employee_rate': emp.prov_rate_employee,
                'employee_amt': slip.amount_provident,
                'employer_rate': emp.prov_rate_employer,
                'employer_amt': slip.amount_provident,
            }
            no+=1
            lines.append(line)
        #settings=get_model("settings").browse(1)
        setting=get_model("hr.payroll.settings").browse(1)
        document_date=utils.date2thai(time.strftime("%Y-%m-%d"),'%(d)s/%(m)s/%(BY)s')
        data={
            'company_name': comp.name,
            'document_date': document_date,
            'fund_name': setting.prov_name,
            'lines': lines,
            'norecord': False if lines else True,
        }
        return data

Report.register()
