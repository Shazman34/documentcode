from netforce.model import Model,fields,get_model 

class Settings(Model):
    _inherit="settings"
    _fields={
        "gst_self_bill_no": fields.Char("GST Self-Billing Approval Number"),
    }

Settings.register()
