from netforce.model import Model,fields,get_model
import time

class Homework(Model):
    _name="ed.homework"
    _string="Homework"
    _name_field="title"
    _fields={
        "date": fields.Date("Date",required=True,search=True),
        "title": fields.Char("Title",required=True,search=True),
        "group_id": fields.Many2One("ed.group","Group",required=True,search=True),
        "course_id": fields.Many2One("ed.course","Course",required=True,search=True),
        "description": fields.Text("Description",search=True),
        "file": fields.File("File"),
        "files": fields.Text("Files"),
    }
    _defaults={
        "date": lambda *a: time.strftime("%Y-%m-%d"),
    }

Homework.register()
