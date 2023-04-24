from netforce.model import Model,fields,get_model
import time

class Student(Model):
    _name="ed.student"
    _string="Student"
    _fields={
        "first_name": fields.Char("First Name",required=True,search=True,translate=True),
        "middle_name": fields.Char("Middle Name",search=True,translate=True),
        "last_name": fields.Char("Last Name",required=True,search=True,translate=True),
        "gender": fields.Selection([["m","Male"],["f","Female"]],"Gender",required=True,search=True,translate=True),
        "blood_group": fields.Selection([["A","A"],["B","B"],["O","O"]],"Blood Group"),
        "birth_date": fields.Date("Date Of Birth",required=True,search=True),
        "country_id": fields.Many2One("country","Nationality",required=True),
        "religion": fields.Char("Religion"),
        "apply_date": fields.Date("Application Date",required=True),
        "addresses": fields.One2Many("address","related_id","Addresses"),
        "groups": fields.Many2Many("ed.group","Groups"),
    }

    def name_get(self,ids,context={}):
        res=[]
        for obj in self.browse(ids):
            name="%s %s"%(obj.first_name,obj.last_name)
            res.append([obj.id,name])
        return res

Student.register()
