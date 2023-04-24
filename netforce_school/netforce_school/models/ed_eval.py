from netforce.model import Model,fields,get_model
import time

class Eval(Model):
    _name="ed.eval"
    _string="Evaluation"
    _name_field="title"
    _fields={
        "date": fields.Date("Date",required=True,search=True),
        "title": fields.Char("Title",required=True,search=True),
        "course_id": fields.Many2One("ed.course","Course"),
        "teacher_id": fields.Many2One("ed.teacher","Teacher"),
        "results": fields.One2Many("ed.eval.result","eval_id","Results"),
        "max_score": fields.Decimal("Maximum Score"),
    }
    _defaults={
        "date": lambda *a: time.strftime("%Y-%m-%d"),
    }

Eval.register()
