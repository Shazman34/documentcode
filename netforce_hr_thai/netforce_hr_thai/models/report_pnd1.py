import time
from netforce.model import Model, fields, get_model
from . import utils
from netforce.access import get_active_company

class Report(Model):
    _name="report.pnd1"
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

        if len(payslip_line) < 1:
            raise Exception("No data available")

        return payslip_line
    
    def print_cover(self,ids,context={}):
        obj=self.browse(ids)[0]
        payslip_line=self.get_payslip_line(obj.month)

        return {
            "next": {
                "name": "report_pnd1_cover_pdf",
                "month": obj.month,
            }
        }

    def print_attach(self,ids,context={}):
        obj=self.browse(ids)[0]
        payslip_line=self.get_payslip_line(obj.month)
        return {
            "next": {
                "name": "report_pnd1_attach_pdf",
                "month": obj.month,
            }
        }

    def get_data(self,context={}):
        company_id=get_active_company()
        comp=get_model("company").browse(company_id)
        month=context.get("month")

        date2thai=utils.date2thai
        wht_items=[
            ('01', '40 (1) in general cases'),
            ('03', '40 (1) (2) termination of employment'),
            ('04', '40 (2) resident of Thailand'),
            ('05', '40 (2) non-resident of Thailand'),
            ]

        lines=[]
        for slip in self.get_payslip_line(month):
            emp=slip.employee_id
            emp_name=' '.join(s for s in [(emp.title and emp.title+'.' or ''),(emp.first_name or ''),(emp.last_name or '')])
            line={
                "line_name": emp_name,
                "line_pin": emp.tax_no,
                "line_date": slip.date and date2thai(slip.date,format='%(d)s/%(m)s/%(BY)s') or '',
                "line_base": slip.amount_wage+slip.amount_allow,
                "line_tax": slip.amount_tax,
                "line_wht_item": wht_items[0][0],
                "line_cond": "1",
            }
            # only who have income
            if line['line_base'] > 0:
                lines.append(line)

        document_date=date2thai(time.strftime("%Y-%m-%d"),'%(d)s,%(Tm)s,%(BY)s').split(',')
        settings=get_model("settings").browse(1)
        address=settings.addresses and settings.addresses[0] or None


        data={
            "pin": settings.tax_no,
            "period": int(month[5:7]),
            "company": comp.name,
            "year": document_date[2],
            "document_date": document_date,
            'depart_room_number': '',
            'depart_stage': address.floor if address else '',
            'depart_village': address.village if address else '',
            'depart_name': address.bldg_name if address else '',
            'depart_number': address.bldg_no if address else '',
            'depart_sub_number': '',
            'depart_soi': address.soi if address else '',
            'depart_road': address.street if address else '',
            'depart_district': '',
            'depart_sub_district': address.sub_district if address else '',
            'depart_province': address.city if address else '',
            'depart_zip': address.postal_code if address else '',
            'depart_tel': '',
            'depart_phone': '',
            "lines": lines,
            'norecord': False if lines else True,
        }

        return data

Report.register()
