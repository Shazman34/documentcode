from netforce.model import Model,fields,get_model

class EnterToken(Model):
    _name="bank.feed.enter.token"
    _transient=True
    _fields={
        "token": fields.Char("Token",required=True),
        "proc_id": fields.Char("Proc ID"),
        "feed_id": fields.Many2One("bank.feed","Bank Feed"),
    }
    _defaults={
        "proc_id": lambda self,ctx: ctx.get("proc_id"),
        "feed_id": lambda self,ctx: ctx.get("feed_id"),
    }

    def do_import(self,ids,context={}):
        print("EnterToken.do_import")
        obj=self.browse(ids[0])
        token=obj.token
        print("Token: %s"%token)
        proc_id=obj.proc_id
        print("ProcID: %s"%proc_id)
        return obj.feed_id.import_continue(proc_id,token)

EnterToken.register()
