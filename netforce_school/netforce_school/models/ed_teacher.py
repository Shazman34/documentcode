from netforce.model import Model,fields,get_model
import time

class Teacher(Model):
    _name="ed.teacher"
    _string="Teacher"
    _fields={
        "first_name": fields.Char("First Name",required=True,search=True,translate=True),
        "last_name": fields.Char("Last Name",required=True,search=True,translate=True),
        "gender": fields.Selection([["m","Male"],["f","Female"]],"Gender",required=True,search=True,translate=True),
    }

    def name_get(self,ids,context={}):
        res=[]
        for obj in self.browse(ids):
            name="%s %s"%(obj.first_name,obj.last_name)
            res.append([obj.id,name])
        return res

Teacher.register()
