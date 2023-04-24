import time
from netforce.model import Model, fields, get_model
from . import utils
from netforce.access import get_active_company

class Report(Model):
    _name="report.pnd91"
    _transient=True
    _fields={
        "year": fields.Date("Year"),
        "employee_id": fields.Many2One("hr.employee","Employee"),
    }
    _defaults={
        "year": lambda *a: time.strftime("%Y-%m-%d"),
    }
    
    def get_default_lines(self):
        # copy data structure from thai payroll
        return {'A1': 0.0,
            'A10': 0.0,
            'A11': 0.0,
            'A12': 0.0,
            'A2': 0.0,
            'A3': 0.0,
            'A4': 0.0,
            'A5': 0.0,
            'A6': 30000.0,
            'A7': 0.0,
            'A8': 0.0,
            'A9': 0.0,
            'B1': 0.0,
            'B2': 0.0,
            'B3': 0.0,
            'B4a': 0.0,
            'B4b': 0.0,
            'B5': 0.0,
            'B6': 0.0,
            'C1': 30000.0,
            'C10': 0.0,
            'C11': 0.0,
            'C12': 0.0,
            'C13': 0.0,
            'C14': 30000.0,
            'C2': 0.0,
            'C3a': 0.0,
            'C3a_persons': 0,
            'C3b': 0.0,
            'C3b_persons': 0,
            'C4a': 0.0,
            'C4b': 0.0,
            'C4c': 0.0,
            'C4d': 0.0,
            'C5': 0.0,
            'C6': 0.0,
            'C7a': 0.0,
            'C7b': 0.0,
            'C8': 0.0,
            'C9': 0.0,
            'birthdate': '',
            'id': 0,
            'name': '',
            'pin': '',
            'spouse_birthdate': '',
            'spouse_name': '',
            'spouse_pin': '',
            }

    def print_pnd91_cover(self,ids,context={}):
        obj=self.browse(ids)[0]
        employee_id=obj.employee_id and int(obj.employee_id.id) or None
        return {
            "next": {
                "name": "report_pnd91_cover_pdf",
                "year": obj.year,
                "employee_id": employee_id,
            }
        }

    def print_pnd91_attach(self,ids,context={}):
        obj=self.browse(ids)[0]
        employee_id=obj.employee_id and int(obj.employee_id.id) or None
        return {
            "next": {
                "name": "report_pnd91_attach_pdf",
                "year": obj.year,
                "employee_id": employee_id,
            }
        }

    def get_data_cover(self,context={}):
        lines=[]
        emp_ids=[]
        employee=get_model('hr.employee')
        date2thai=utils.date2thai
        if context.get('employee_id')!='null':
           emp_ids=[int(context.get('employee_id'))]
        else:
            emp_ids=employee.search([])

        choice={"spouse_status": {"married": "01", "married_new": "02","divorced": "03", "deceased": "04"},
                "marital_status": {"single": "01", "married": "02", "divorced": "03", "widowed": "04"},
                }

        for emp in employee.browse(emp_ids):
            emp_name=" ".join(s for s in [(emp.title and emp.title+'.' or ''),(emp.first_name or ''),(emp.last_name or '')])
            spouse_name=" ".join(s for s in [(emp.spouse_title and emp.spouse_title+'.' or ''),(emp.spouse_first_name or ''),(emp.spouse_last_name or '')])
            address=emp.addresses and emp.addresses[0] or None
            line={
                'pin': emp.tax_no,
                'name': emp_name,
                'birthdate': emp.birth_date and date2thai(emp.birth_date,format='%(d)s/%(m)s/%(BY)s') or '',
                'spouse_pin': emp.spouse_tax_no,
                'spouse_name': spouse_name,
                'spouse_birthdate': emp.spouse_birth_date and date2thai(emp.spouse_birth_date,format='%(d)s/%(m)s/%(BY)s') or '',
                'spouse_status': choice['spouse_status'][emp.spouse_status] if emp.spouse_status else '',
                'person_tax_status': choice['marital_status'][emp.marital_status] if emp.marital_status else '',
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
            }
            lines.append(line)
        document_date=date2thai(time.strftime("%Y-%m-%d"),'%(d)s,%(Tm)s,%(BY)s').split(',')
        data={
            "document_date": document_date,
            "year": document_date[2],
            'norecord': False if lines else True,
            "lines": lines,
        }
        return data

    def get_data_attach(self,context={}):
        company_id=get_active_company()
        comp=get_model("company").browse(company_id)
        lines=[]
        emp_ids=[]
        date2thai=utils.date2thai
        employee=get_model('hr.employee')
        if context.get('employee_id')!='null':
           emp_ids=[int(context.get('employee_id'))]
        else:
            emp_ids=employee.search([])

        for emp in employee.browse(emp_ids):
            context['employee_id']=emp.id
            tax=get_model("hr.payitem").compute_thai_tax(context=context)
            line=self.get_default_lines()
            line['pin']=emp.tax_no
            # update tax 
            for k,v in tax.items():
                if k == 'C3a':
                    line['C3a_persons'] = emp.num_child1
                elif k == 'C3b':
                    line['C3b_persons'] = emp.num_child2
                line[k]=v
            lines.append(line)
        settings=get_model("settings").browse(1)
        document_date=date2thai(time.strftime("%Y-%m-%d"),'%(d)s,%(Tm)s,%(BY)s').split(',')
        data={
            "company": comp.name,
            "pin": settings.tax_no,
            "document_date": document_date,
            'norecord': False if lines else True,
            "year": document_date[2],
            "lines": lines,
        }
        return data

Report.register()
