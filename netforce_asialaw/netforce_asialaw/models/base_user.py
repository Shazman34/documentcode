from netforce.model import Model,get_model,fields

class User(Model):
    _inherit="base.user"
    _fields={
        "aln_client_id": fields.Many2One("aln.client","Client"),
        "aln_lawyer_id": fields.Many2One("aln.lawyer","Lawyer"),
    }

User.register()
