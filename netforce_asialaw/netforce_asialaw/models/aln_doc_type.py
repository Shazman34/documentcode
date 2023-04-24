from netforce.model import Model,fields,get_model

class DocType(Model):
    _name="aln.doc.type"
    _string="Document Type"
    _fields={
        "name": fields.Char("Document Type Name",search=True),
    }

DocType.register()
