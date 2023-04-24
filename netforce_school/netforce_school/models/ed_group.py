from netforce.model import Model,fields,get_model
import time

class Group(Model):
    _name="ed.group"
    _string="Student Group"
    _fields={
        "name": fields.Char("Group Name",required=True,search=True),
        "description": fields.Text("Description",search=True),
        "students": fields.Many2Many("ed.student","Students"),
        "num_students": fields.Integer("Number Of Students",function="get_num_students"),
    }

    def get_num_students(self,ids,context={}):
        vals={}
        for obj in self.browse(ids):
            vals[obj.id]=len(obj.students)
        return vals

Group.register()
