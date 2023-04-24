from netforce.model import get_model
from netforce import config
from netforce import database
from netforce import access
from netforce import utils
from pyftpdlib.handlers import FTPHandler
from pyftpdlib.servers import FTPServer
from pyftpdlib.authorizers import DummyAuthorizer, AuthenticationFailed
from pyftpdlib.filesystems import AbstractedFS
from multiprocessing import Process
from collections import namedtuple
import os.path
import io
import tempfile
from datetime import *
import time
import calendar

FTP_PORT=2121

class NFAuthorizer(DummyAuthorizer):
    def __init__(self):
        super().__init__()
        self.schema=None
        self.user_id=None

    def validate_authentication(self, username, password, handler):
        print("NFAuthorizer.validate_authentication",username)
        dbname = config.get("database")
        if not dbname:
            raise Exception("No active database")
        print("dbname",dbname)
        database.set_active_db(dbname)
        if username.find("org_")!=-1: # XXX
            schema,_,login=username.partition(".")
            print("schema",schema)
            print("login",login)
            database.set_active_schema(schema)
        else:
            schema=None
            login=username
        with database.Transaction():
            db=database.get_connection()
            res=db.get("SELECT id,password FROM base_user WHERE login=%s",login)
            if not res:
                raise AuthenticationFailed
            enc_pass=res.password
            if not utils.check_password(password,enc_pass):
                raise AuthenticationFailed
            handler.nf_schema=schema
            handler.nf_user_id=res.id
            print("Login success!")

    def get_home_dir(self,username):
        return "/"

    def get_msg_login(self,username):
        return "Welcome to Netforce."

    def get_msg_quit(self,username):
        return "Goodbye, thank you for using Netforce."

    def has_perm(self, username, perm, path=None):
        return True

class NFHandler(FTPHandler):
    def __init__(self,*args,**kwargs):
        print("NFHandler.__init__")
        super().__init__(*args,**kwargs)
        self.nf_user_id=None
        self.nf_schema=None
    
    def process_command(self, cmd, *args, **kwargs):
        print("#"*80)
        print("NFHandler.process_command",cmd,args,kwargs)
        if self.nf_user_id:
            dbname = config.get("database")
            if not dbname:
                raise Exception("No active database")
            print("dbname",dbname)
            database.set_active_db(dbname)
            database.set_active_schema(self.nf_schema)
            access.set_active_user(self.nf_user_id)
        if cmd in ["LIST","SIZE","RETR","STOR"]:
            with database.Transaction():
                return super().process_command(cmd,*args,**kwargs)
        else:
            return super().process_command(cmd,*args,**kwargs)

class NFFile:
    def __init__(self,filename,model,active_id,vals,field,handler):
        print("NFFile.__init__",filename)
        self.f=io.BytesIO()
        self.name=filename
        self.closed=False
        self.model=model
        self.active_id=active_id
        self.vals=vals
        self.field=field
        self.handler=handler

    def write(self,data):
        print("NFFile.write",data)
        self.f.write(data)

    def close(self):
        print("NFFile.close")
        print("$"*80)
        print("$"*80)
        print("$"*80)
        data=self.f.getvalue()
        self.vals[self.field]=data.decode("utf-8")
        if not self.handler.nf_user_id:
            raise Exception("Missing user_id")
        dbname = config.get("database")
        if not dbname:
            raise Exception("No active database")
        print("dbname",dbname)
        database.set_active_db(dbname)
        database.set_active_schema(self.handler.nf_schema)
        access.set_active_user(self.handler.nf_user_id)
        with database.Transaction():
            if self.active_id:
                print("write",self.model,self.active_id,self.vals)
                get_model(self.model).write([self.active_id],self.vals)
            else:
                print("create",self.model,self.vals)
                get_model(self.model).create(self.vals)
        self.closed=True

class NFFilesystem(AbstractedFS):
    def chdir(self,path):
        print("NFFilesystem.chdir",path)
        self._cwd = self.fs2ftp(path)

    def mkdir(self,path):
        print("NFFilesystem.mkdir",path)
        raise Exception("Not implemented")

    def listdir(self,path):
        print("NFFilesystem.listdir",path)
        comps=path.split("/")[1:]
        if len(comps)==1 and comps[0]=="":
            return ["themes"]
        elif len(comps)==1 and comps[0]=="themes":
            data=[]
            for obj in get_model("theme").search_browse([]):
                data.append(obj.name)
            return data
        elif len(comps)==2 and comps[0]=="themes":
            return ["components","static"]
        elif len(comps)==3 and comps[0]=="themes" and comps[2]=="components":
            theme=comps[1]
            data=[]
            for obj in get_model("theme.component").search_browse([["theme_id.name","=",theme]]):
                data.append(obj.name)
            return data
        elif len(comps)==3 and comps[0]=="themes" and comps[2]=="static":
            data=[]
            for obj in get_model("theme.file").search_browse([["theme_id.name","=",theme]]):
                n=os.path.basename(obj.name) # XXX
                data.append(n)
            return data
        else:
            raise Exception("Invalid directory: %s"%path)

    def rmdir(self,path):
        print("NFFilesystem.rmdir",path)
        raise Exception("Not implemented")

    def remove(self,path):
        print("NFFilesystem.remove",path)
        raise Exception("Not implemented")

    def rename(self,src,dst):
        print("NFFilesystem.rename",src,dst)
        raise Exception("Not implemented")

    def chmod(self,path,mode):
        print("NFFilesystem.chmod",path,mode)

    def stat(self,path):
        print("NFFilesystem.stat",path)
        o=namedtuple("stat",["st_mode"])
        if self.isdir(path):
            o.st_mode=0o40744
        else:
            o.st_mode=0o10644
        o.st_nlink=None
        o.st_size=self.getsize(path)
        o.st_uid=0
        o.st_gid=0
        o.st_mtime=self._get_mtime(path)
        return o

    lstat=stat 

    def isfile(self, path):
        print("NFFilesystem.isfile",path)
        return not self.isdir(path)

    def islink(self, path):
        print("NFFilesystem.islink",path)
        raise Exception("Not implemented")

    def isdir(self, path):
        print("NFFilesystem.isdir",path)
        comps=path.split("/")[1:]
        if len(comps)==1 and comps[0]=="":
            return True
        elif len(comps)==1 and comps[0]=="themes":
            return True
        elif len(comps)==2 and comps[0]=="themes":
            return True
        elif len(comps)==3 and comps[0]=="themes" and comps[2]=="components":
            return True
        elif len(comps)==3 and comps[0]=="themes" and comps[2]=="static":
            return True
        return False

    def getsize(self, path):
        print("NFFilesystem._getsize",path)
        comps=path.split("/")[1:]
        if len(comps)==4 and comps[0]=="themes" and comps[2]=="components":
            theme=comps[1]
            name=comps[3]
            res=get_model("theme.component").search([["theme_id.name","=",theme],["name","=",name]])
            if not res:
                raise Exception("Invalid path")
            comp_id=res[0]
            comp=get_model("theme.component").browse(comp_id)
            return len(comp.body)
        return 0;

    def _get_mtime(self, path):
        print("NFFilesystem._get_mtime",path)
        comps=path.split("/")[1:]
        if len(comps)==4 and comps[0]=="themes" and comps[2]=="components":
            theme=comps[1]
            name=comps[3]
            res=get_model("theme.component").search([["theme_id.name","=",theme],["name","=",name]])
            if not res:
                raise Exception("Invalid path")
            comp_id=res[0]
            comp=get_model("theme.component").browse(comp_id)
            return calendar.timegm(datetime.strptime(comp.write_time,"%Y-%m-%d %H:%M:%S").timetuple())
        return 0;

    def getmtime(self, path):
        print("NFFilesystem.getmtime",path)
        raise Exception("Not implemented")

    def realpath(self, path):
        print("NFFilesystem.realpath",path)
        return path

    def lexists(self, path):
        print("NFFilesystem.lexists",path)
        raise Exception("Not implemented")

    def get_user_by_uid(self, uid):
        print("NFFilesystem.get_user_by_uid",uid)
        return "user"

    def get_group_by_gid(self, gid):
        print("NFFilesystem.get_group_by_gid",gid)
        return "group"

    def open(self, filename, mode):
        print("NFFilesystem.open",filename,mode)
        comps=filename.split("/")[1:]
        if len(comps)==4 and comps[0]=="themes" and comps[2]=="components":
            theme=comps[1]
            name=comps[3]
            res=get_model("theme").search([["name","=",theme]])
            if not res:
                raise Exception("Invalid theme: %s"%theme)
            theme_id=res[0]
            if mode=="rb":
                res=get_model("theme.component").search([["theme_id","=",theme_id],["name","=",name]])
                if not res:
                    raise Exception("Invalid path")
                comp_id=res[0]
                comp=get_model("theme.component").browse(comp_id)
                f=tempfile.TemporaryFile()
                f.write(comp.body.encode("utf-8"))
                f.seek(0)
                return f
            elif mode=="wb":
                res=get_model("theme.component").search([["theme_id","=",theme_id],["name","=",name]])
                if res:
                    active_id=res[0]
                else:
                    active_id=None
                vals={"theme_id":theme_id,"name":name}
                f=NFFile(filename,"theme.component",active_id,vals,"body",self.cmd_channel)
                return f
            else:
                raise Exception("Invalid mode")
        else:
            raise Exception("Invalid path")


def serve_ftp():
    config.load_config() # XXX
    authorizer=NFAuthorizer()
    handler=NFHandler
    handler.authorizer=authorizer
    handler.abstracted_fs=NFFilesystem
    server=FTPServer(("",FTP_PORT),handler)
    server.serve_forever()

ftp_proc=Process(target=serve_ftp)
ftp_proc.start()
