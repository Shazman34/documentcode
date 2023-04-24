from netforce.model import Model,fields,get_model

class Cell(Model):
    _name="nd.cell"
    _string="Cell"
    _fields={
        "cid": fields.Char("Cell ID"),
        "lac": fields.Char("Location Area Code"),
        "mcc": fields.Char("Mobile Country Code"),
        "mnc": fields.Char("Mobile Network Code"),
        "coords": fields.Char("Coordinates"),
        "accuracy": fields.Float("Accuracy"),
    }

Cell.register()
