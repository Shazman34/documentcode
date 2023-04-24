from netforce.model import Model, fields, get_model

class RequiredDoc(Model):
    _name="jc.required.doc"
    _string="Required Document"
    _fields={
        "name": fields.Text("Document Name",required=True),
        "related_id": fields.Reference([],"Related To"),
    }

RequiredDoc.register()
