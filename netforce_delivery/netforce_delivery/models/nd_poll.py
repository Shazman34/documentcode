from netforce.model import Model,fields,get_model

class Poll(Model):
    _name="nd.poll"
    _string="Poll"
    _fields={
        "name": fields.Char("Question",required=True),
        "options": fields.One2Many("nd.poll.option","poll_id","Options"),
        "answers": fields.One2Many("nd.poll.answer","poll_id","Customer Answers"),
        "num_options": fields.Integer("# options",function="get_num_options"),
        "num_answers": fields.Integer("# answers",function="get_num_answers"),
    }

    def get_num_options(self,ids,context={}):
        vals={}
        for obj in self.browse(ids):
            vals[obj.id]=len(obj.options)
        return vals

    def get_num_answers(self,ids,context={}):
        vals={}
        for obj in self.browse(ids):
            vals[obj.id]=len(obj.answers)
        return vals

Poll.register()
