from netforce.model import Model,fields,get_model

class Tag(Model):
    _name="nd.tag"
    _string="Tag"
    _fields={
        "name": fields.Char("Tag Name",required=True),
        "color": fields.Char("Color"),
        "description": fields.Text("Description"),
    }

Tag.register()
