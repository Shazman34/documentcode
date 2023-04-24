from netforce.model import Model,fields,get_model


class Settings(Model):
    _inherit="settings"
    _fields={
    }

Settings.register()
