from netforce import database
from netforce.model import get_model
from netforce import access
from netforce import tasks
from netforce import config
import time

config.load_config()

old_run_tasks=tasks.run_tasks

def get_db_names():
    database.set_active_db("template1")
    with database.Transaction():
        db=database.get_connection()
        res=db.query("SELECT datname FROM pg_database WHERE datistemplate=false")
        names=[r.datname for r in res if r.datname.startswith("nfo_")]
        return names

def create_cron_job_tasks(db_names):
    for dbname in db_names:
        print("#"*80)
        print("DB %s"%dbname)
        database.set_active_db(dbname)
        with database.Transaction():
            access.set_active_user(1)
            job_ids=get_model("cron.job").search([["state","=","active"]])
            get_model("cron.job").update_dates(job_ids)
            get_model("cron.job").create_tasks(job_ids)

def run_tasks():
    db_names=get_db_names()
    print("db_names",db_names)
    create_cron_job_tasks(db_names)
    t=time.strftime("%Y-%m-%d %H:%M:%S")
    for dbname in db_names:
        tasks.db_tasks[dbname]=t
    old_run_tasks()

tasks.run_tasks=run_tasks
