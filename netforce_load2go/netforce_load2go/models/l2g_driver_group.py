from netforce.model import Model,fields,get_model
import time

class DriverGroup(Model):
    _name="l2g.driver.group"
    _string="Driver Group"
    _fields={
        "name": fields.Char("Group Name",required=True),
    }

DriverGroup.register()
