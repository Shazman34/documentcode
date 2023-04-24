from netforce.model import Model,fields,get_model
import time

class Meal(Model):
    _name="ed.meal"
    _string="Meal"
    _name_field="title"
    _fields={
        "date": fields.Date("Date",required=True,search=True),
        "time": fields.Char("Time",required=True),
        "title": fields.Char("Title",required=True,search=True),
        "image": fields.File("Image"),
        "description": fields.Text("Description",search=True),
        "group_id": fields.Many2One("ed.group","Group"),
    }
    _defaults={
        "date": lambda *a: time.strftime("%Y-%m-%d"),
    }

Meal.register()
