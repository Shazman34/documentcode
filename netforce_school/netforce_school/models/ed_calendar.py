from netforce.model import Model,fields,get_model
import time

class Calendar(Model):
    _name="ed.calendar"
    _string="Calendar Day"
    _fields={
        "date": fields.Date("Date",required=True,search=True),
        "type": fields.Selection([["school_term","School Terms"],["school_holiday","School Holidays"],["public_holiday","Public Holidays"]],"Type",required=True,search=True),
        "title": fields.Char("Title",search=True),
    }
    _defaults={
        "date": lambda *a: time.strftime("%Y-%m-%d"),
    }

Calendar.register()
