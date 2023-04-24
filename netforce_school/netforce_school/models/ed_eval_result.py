from netforce.model import Model,fields,get_model
import time

class Result(Model):
    _name="ed.eval.result"
    _string="Evaluation Result"
    _fields={
        "eval_id": fields.Many2One("ed.eval","Evaluation",required=True,search=True,on_delete="cascade"),
        "student_id": fields.Many2One("ed.student","Student",required=True,search=True),
        "score": fields.Decimal("Result Score"),
    }

Result.register()
