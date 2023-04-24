from netforce.model import Model,fields,get_model
from netforce import utils
from netforce import tasks
import fdb

class Sync(Model):
    _name="sqla.sync"
    _fields={
        "file": fields.File("FDB File",required=True),
        "imp_acc": fields.Boolean("Import Accounts"),
    }

    def merge_account(self,vals,context={}):
        res=get_model("account.account").search([["code","=",vals["code"]]])
        if res:
            account_id=res[0]
            get_model("account.account").write([account_id],vals)
        else:
            account_id=get_model("account.account").create(vals)
        return account_id

    def do_import(self,ids,context={}):
        obj=self.browse(ids[0])
        if not file:
            raise Exception("File is missing")
        job_id=context.get("job_id")
        USER="sysdba"
        PASSWORD="sqlblabla"
        path=utils.get_file_path(obj.file)
        con=fdb.connect(dsn=path,user=USER,password=PASSWORD)
        if obj.imp_acc:
            cur=con.cursor()
            cur.execute("select count(*) from gl_acc")
            res=cur.fetchone()
            num_accounts=res[0]
            cur.execute("select code,description from gl_acc")
            for i,r in enumerate(cur.itermap()):
                if job_id:
                    if tasks.is_aborted(job_id):
                        return
                    tasks.set_progress(job_id,i*100/len(d),"Importing account %s of %s."%(i+1,num_accounts))
                code=r["code"].strip()
                name=r["code"].strip() or "/"
                #parent=r["parent"].strip()
                parent=None
                type=None
                if code[0]=="1":
                    type="cur_asset"
                elif code[0]=="2":
                    type="cur_liability"
                elif code[0]=="3":
                    type="equity"
                elif code[0]=="4":
                    type="revenue"
                else:
                    type="expense"
                if parent:
                    res=get_model("account.account").search([["code","=",parent]])
                    if not res:
                        raise Exception("Parent not found: %s"%parent)
                    parent_id=res[0]
                else:
                    parent_id=None
                self.merge_account({"code":code,"name":name,"type":type,"parent_id":parent_id})

Sync.register()
