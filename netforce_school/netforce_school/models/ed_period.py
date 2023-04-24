from netforce.model import Model,fields,get_model
import time

class Period(Model):
    _name="ed.period"
    _string="Period"
    _fields={
        "name": fields.Char("Period Name",required=True,search=True),
        "date_from": fields.Date("From Date",required=True),
        "date_to": fields.Date("To Date",required=True),
    }
    _defaults={
    }

Period.register()
