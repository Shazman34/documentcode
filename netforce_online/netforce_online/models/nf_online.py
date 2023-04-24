from netforce.model import Model,fields,get_model,update_db
from netforce import database
import os

class Online(Model):
    _name="nf.online"
    _store=False

    def create_schema(self,name):
        print("Online.create_schema",name)
        db=database.get_connection()
        db.execute("CREATE SCHEMA %s"%name)
        db.commit()
        os.system("cat /home/datrus/online/nf_template.sql | sed 's/org_23/%s/g' | psql -d nfonline"%name)
        #db.commit() # XXX: need to commit because connection will change after set active schema
        #print("schema created")
        #database.set_active_schema(name)
        #with database.Transaction():
        #    update_db(force=True)

Online.register()
