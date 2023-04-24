from netforce.model import Model, fields, get_model

class TaskStage(Model):
    _name="jc.task.stage"
    _string="Task Stage"
    _fields={
        "service_id": fields.Many2One("jc.service","Service",required=True,search=True),
        "name": fields.Char("Name",required=True,search=True),
        "sequence": fields.Integer("Sequence"),
        "active": fields.Boolean("Active"),
        "comments": fields.One2Many("message","related_id","Comments"),
    }
    _order="service_id,sequence"
    _defaults={
        "active": True,
    }

TaskStage.register()
