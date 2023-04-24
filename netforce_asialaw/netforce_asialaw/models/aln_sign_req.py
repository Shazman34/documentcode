from netforce.model import Model,fields,get_model
from netforce import utils
import time
import os
import json
import random

class SignReq(Model):
    _name="aln.sign.req"
    _string="Signing Request"
    _fields={
        "date": fields.Date("Date",required=True),
        "client_id": fields.Many2One("aln.client","Client",required=True),
        "job_id": fields.Many2One("aln.job","Job",required=True,search=True),
        "task_id": fields.Many2One("aln.task","Task",required=True,search=True),
        "file": fields.File("Document File"),
        "state": fields.Selection([["draft","Draft"],["wait_sign","Awaiting Signature"],["done","Signed"]],"Status",required=True),
        "data": fields.Text("Data"),
    }
    _order="date desc,id desc"
    _defaults={
        "date": lambda *a: time.strftime("%Y-%m-%d"),
        "state": "draft",
    }

    def prepare_doc(self,ids,context={}):
        obj=self.browse(ids[0])
        if not obj.file:
            raise Exception("Missing document file")
        if not obj.file.lower().endswith(".pdf"):
            raise Exception("Only PDF document files are support at the moment.")
        if not obj.data:
            path=utils.get_file_path(obj.file)
            rand=random.randint(0,9999)
            prefix="sign-req-%d-%.4d"%(obj.id,rand)
            dir_path=os.path.dirname(path)
            os.system("cd %s; convert -density 150 %s %s.png"%(dir_path,obj.file,prefix))
            images=[]
            for fname in os.listdir(dir_path):
                if fname.startswith(prefix):
                    images.append(fname)
            images.sort()
            data={"images":images}
            obj.write({"data":json.dumps(data)})
        return {
            "next": {
                "name": "aln_prepare_sign",
                "active_id": obj.id,
            }
        }

    def request_sig(self,ids,context={}):
        obj=self.browse(ids[0])
        obj.write({"state":"wait_sign"})

    def to_draft(self,ids,context={}):
        obj=self.browse(ids[0])
        obj.write({"state":"draft","data":None})
        
SignReq.register()
