from netforce.model import Model,fields,get_model

class User(Model):
    _inherit="base.user"
    _fields={
        "gt_customer_id": fields.Many2One("gt.customer","Gold Trade Customer"),
    }

User.register()
