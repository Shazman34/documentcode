from netforce.model import Model,fields,get_model

class JobType(Model):
    _name="aln.job.type"
    _string="Job Type"
    _fields={
        "name": fields.Char("Job Type Name",required=True),
    }

JobType.register()
