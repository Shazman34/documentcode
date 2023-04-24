from netforce.model import Model,fields,get_model

class Article(Model):
    _name="hd.article"
    _string="Article"
    _fields={
        "title": fields.Char("Title",required=True,search=True),
        "body": fields.Text("Body",search=True),
        "sequence": fields.Integer("Sequence"),
        "categ_id": fields.Many2One("hd.categ","Category",required=True,search=True),
        "state": fields.Selection([["draft","Draft"],["published","Published"]],"Status",required=True,search=True),
        "short_name": fields.Char("Short Name"),
    }
    _order="sequence"
    _defaults={
        "state": "draft",
    }

    def do_search(self,q,context={}):
        words=[w.strip() for w in q.split()]
        cond=[]
        for w in words:
            cond.append(["or",["title","ilike",w],["body","ilike",w]])
        data=self.search_read(cond)
        vals={
            "query": q,
            "num_results": len(data),
        }
        if context.get("ip_addr"):
            vals["ip_addr"]=context["ip_addr"]
        get_model("hd.query").create(vals)
        return data

Article.register()   
