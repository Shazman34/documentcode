from netforce.model import Model,fields,get_model
import time

class Document(Model):
    _inherit="document"

    def default_get(self,*a,**kw):
        print("bkkbase Document.default_get")
        res=super().default_get(*a,**kw)
        context=kw.get("context",{})
        defaults=context.get("defaults")
        if defaults:
            related_id=defaults.get("related_id")
            if related_id:
                model,model_id=related_id.split(",")
                model_id=int(model_id)
                if model=="job":
                    job=get_model("job").browse(model_id)
                    res["contact_id"]=job.contact_id.id
        date=res.get("date")
        if not date:
            res["date"]=time.strftime("%Y-%m-%d %H:%M:%S")
        print("res",res)
        return res

Document.register()
