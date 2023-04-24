from netforce.model import Model,fields,get_model

class Round(Model):
    _name="nd.round"
    _string="Delivery Round"
    _fields={
        "driver_id": fields.Many2One("nd.driver","Driver",required=True,search=True),
        "period_id": fields.Many2One("nd.work.period","Work Period",required=True,search=True),
        "seq_from": fields.Integer("From Sequence"),
        "seq_to": fields.Integer("To Sequence"),
        "user_id": fields.Many2One("base.user","Reponsible User"),
    }
    _order="seq_from"

    def name_get(self,ids,context={}):
        res=[]
        for obj in self.browse(ids):
            name="%s-%s"%(obj.driver_id.name,obj.period_id.name)
            res.append([obj.id,name])
        return res

Round.register()
