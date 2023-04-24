from netforce.model import Model,fields,get_model
import requests
import json

class Categ(Model):
    _name="hd.categ"
    _string="Category"
    _fields={
        "name": fields.Char("Name",required=True,search=True),
        "sequence": fields.Integer("Sequence"),
        "include_pdf": fields.Boolean("Include in PDF"),
        "articles": fields.One2Many("hd.article","categ_id","Articles",condition=[["state","=","published"]]),
    }
    _order="sequence"

    def update_pdf(self,context={}):
        print("update_pdf")
        ids=self.search([["include_pdf","=",True]])
        url='https://backend.netforce.com/report?model=hd.categ&template=help_pdf&ids=%s&context={"database":"nfo_help"}'%json.dumps(ids)
        print("url",url)
        r=requests.get(url)
        open("static/db/nfo_help/files/netforce_help.pdf","wb").write(r.content)
        return {
            "flash": "PDF size: %d"%len(r.content),
        }

Categ.register()   
