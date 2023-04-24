from netforce.model import Model,fields,get_model
from netforce import access
from netforce import database
from netforce import utils

class User(Model):
    _inherit="base.user"
    _fields={
        "hx_db_key": fields.Char("DB Key"),
        "hx_plan_id": fields.Many2One("hx.plan","Price Plan"),
    }

User.register()
