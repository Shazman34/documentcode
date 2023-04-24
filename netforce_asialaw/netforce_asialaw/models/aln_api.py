from netforce.model import Model,fields,get_model
from netforce import utils
from netforce import database
from datetime import *
import time
import json

class API(Model):
    _name="aln.api"
    _store=False

    def get_countries(self,context={}):
        data=[]
        for obj in get_model("country").search_browse([]):
            data.append({
                "country_id": obj.id,
                "country_name": obj.name,
                "country_code": obj.code,
                "flag_url": "https://backend.netforce.com/static/db/nfo_asialaw/files/%s"%obj.flag if obj.flag else None,
                "phone_prefix": obj.phone_prefix,
                "timezone": obj.timezone,
            })
        return data

    def get_qc_topics(self,context={}):
        data=[]
        for obj in get_model("aln.qc.categ").search_browse([["parent_id","=",None]]):
            data.append({
                "topic_id": obj.id,
                "title": obj.name,
                "description": obj.short_desc,
                "examples": obj.examples,
                "details": obj.long_desc,
                "image_url": "https://backend.netforce.com/static/db/nfo_asialaw/files/%s"%obj.image if obj.image else None,
            })
        return data

    def get_qc_categs(self,topic_id,context={}):
        if not topic_id:
            raise Exception("Missing topic_id")
        data=[]
        for obj in get_model("aln.qc.categ").search_browse([["parent_id","=",topic_id]]):
            data.append({
                "categ_id": obj.id,
                "title": obj.name,
                "description": obj.short_desc,
                "examples": obj.examples,
                "details": obj.long_desc,
                "image_url": "https://backend.netforce.com/static/db/nfo_asialaw/files/%s"%obj.image if obj.image else None,
            })
        return data

    def get_qc_categ_info(self,categ_id,context={}):
        if not categ_id:
            raise Exception("Missing categ_id")
        obj=get_model("aln.qc.categ").browse(categ_id)
        data={
            "categ_id": obj.id,
            "title": obj.name,
            "description": obj.short_desc,
            "examples": obj.examples,
            "details": obj.long_desc,
            "image_url": "https://backend.netforce.com/static/db/nfo_asialaw/files/%s"%obj.image if obj.image else None,
            "price": 49, # xXX
        }
        return data

    def get_qc_lawyers(self,categ_id,country_id=None,context={}):
        if not categ_id:
            raise Exception("Missing categ_id")
        data=[]
        for obj in get_model("aln.lawyer").search_browse([["qc_categs.id","=",categ_id]]):
            data.append({
                "lawyer_id": obj.id,
                "first_name": obj.first_name,
                "last_name": obj.last_name,
                "designation": obj.designation,
                "firm_name": obj.firm_id.name,
                "about": obj.about,
                "picture_url": "https://backend.netforce.com/static/db/nfo_asialaw/files/%s"%obj.picture if obj.picture else None,
            })
        return data

    def get_reviews(self,lawyer_id,context={}):
        if not lawyer_id:
            raise Exception("Missing lawyer_id")
        data=[]
        for obj in get_model("aln.feedback").search_browse([["lawyer_id","=",lawyer_id]]):
            data.append({
                "review_id": obj.id,
                "rating": obj.rating,
                "remarks": obj.remarks,
                "client_name": obj.client_id.name,
            })
        return data

    def login(self,email,password,context={}):
        user_id = get_model("base.user").check_password(email, password)
        if not user_id:
            raise Exception("Invalid password")
        user=get_model("base.user").browse(user_id)
        dbname=database.get_active_db()
        token=utils.new_token(dbname,user_id)
        return {
            "user_id": user_id,
            "token": token,
            "client_id": user.aln_client_id.id,
            "lawyer_id": user.aln_lawyer_id.id,
        }

    def client_register(self,first_name,last_name,email,phone,country_code,password,confirm_password,context={}):
        if confirm_password!=password:
            raise Exception("Passwords don't match")
        res = get_model("base.user").search([["login","=",email]])
        if res:
            user_id=res[0]
        else:
            res=get_model("profile").search([["code","=","ALN_TEST"]])
            if not res:
                raise Exception("Profile not found")
            profile_id=res[0]
            vals={
                "name": first_name+" "+last_name,
                "login": email,
                "password": password,
                "profile_id": profile_id,
            }
            user_id=get_model("base.user").create(vals)
        user=get_model("base.user").browse(user_id)
        if user.aln_client_id:
            raise Exception("User is already a client")
        res=get_model("country").search([["code","=",country_code]])
        if not res:
            raise Exception("Invalid country code: %s"%country_code)
        country_id=res[0]
        vals={
            "first_name": first_name,
            "last_name": last_name,
            "email": email,
            "phone": phone,
            "country_id": country_id,
        }
        client_id=get_model("aln.client").create(vals)
        client=get_model("aln.client").browse(client_id)
        client.trigger("registered")
        user.write({"aln_client_id":client_id})
        dbname=database.get_active_db()
        token=utils.new_token(dbname,user_id)
        return {
            "user_id": user_id,
            "token": token,
            "client_id": client_id,
        }

    def lawyer_register(self,first_name,last_name,password,email,confirm_password,country_code,phone,designation,type,organization,context={}):
        if confirm_password!=password:
            raise Exception("Passwords don't match")
        res = get_model("base.user").search([["login","=",email]])
        if res:
            user_id=res[0]
        else:
            res=get_model("profile").search([["code","=","ALN_TEST"]])
            if not res:
                raise Exception("Profile not found")
            profile_id=res[0]
            vals={
                "name": first_name+" "+last_name,
                "login": email,
                "password": password,
                "profile_id": profile_id,
            }
            user_id=get_model("base.user").create(vals)
        user=get_model("base.user").browse(user_id)
        if user.aln_lawyer_id:
            raise Exception("User is already a lawyer")
        res=get_model("country").search([["code","=",country_code]])
        if not res:
            raise Exception("Invalid country code: %s"%country_code)
        country_id=res[0]
        res=get_model("aln.firm").search([["name","=",organization]])
        if res:
            firm_id=res[0]
        else:
            vals={
                "name": organization,
            }
            firm_id=get_model("aln.firm").create(vals)
        vals={
            "first_name": first_name,
            "last_name": last_name,
            "email": email,
            "phone": phone,
            "country_id": country_id,
            "designation": designation,
            "type": type,
            "firm_id": firm_id,
        }
        lawyer_id=get_model("aln.lawyer").create(vals)
        lawyer=get_model("aln.lawyer").browse(lawyer_id)
        lawyer.trigger("registered")
        user.write({"aln_lawyer_id":lawyer_id})
        dbname=database.get_active_db()
        token=utils.new_token(dbname,user_id)
        return {
            "user_id": user_id,
            "token": token,
            "lawyer_id": lawyer_id,
        }

    def get_client_info(self,client_id,context={}):
        if not client_id:
            raise Exception("Missing client_id")
        obj=get_model("aln.client").browse(client_id)
        data={
            "client_id": client_id,
            "first_name": obj.first_name,
            "last_name": obj.last_name,
            "email": obj.email,
            "phone": obj.phone,
            "country_id": obj.country_id.id,
            "country_name": obj.country_id.name,
        }
        return data

    def get_lawyer_info(self,lawyer_id,context={}):
        if not lawyer_id:
            raise Exception("Missing lawyer_id")
        obj=get_model("aln.lawyer").browse(lawyer_id)
        data={
            "lawyer_id": lawyer_id,
            "first_name": obj.first_name,
            "last_name": obj.last_name,
            "email": obj.email,
            "phone": obj.phone,
            "qc_phone": obj.qc_phone,
        }
        return data

    def get_qc_call_times(self,lawyer_id,context={}):
        if not lawyer_id:
            raise Exception("Missing lawyer_id")
        slots=["09:30","12:00","18:30"]
        times=[]
        d=datetime.today()+timedelta(days=1)
        while len(times)<6:
            for s in slots:
                t=d.strftime("%Y-%m-%d")+" "+s+":01"
                times.append(t)
            d+=timedelta(days=1)
        return times[:6]

    def qc_place_order(self,client_id,categ_id,lawyer_id,facts,questions,parties,call_times,return_url,cancel_url,context={}):
        vals={
            "origin": "qc",
            "client_id": client_id,
            "lawyer_id": lawyer_id,
            "qc_categ_id": categ_id,
            "facts": facts,
            "questions": questions,
            "parties": parties,
            "call_times": json.dumps(call_times),
        }
        job_id=get_model("aln.job").create(vals)
        res=get_model("payment.method").search([["type","=","paypal"]])
        if not res:
            raise Exception("Paypal payment method not found")
        meth_id=res[0]
        meth=get_model("payment.method").browse(meth_id)
        amount=49 # XXX
        currency_code="SGD"
        res=get_model("currency").search([["code","=",currency_code]])
        if not res:
            raise Exception("Currency not found")
        currency_id=res[0]
        ctx={
            "amount": amount, 
            "currency_id": currency_id,
            "return_url": return_url+"?case_id=%s"%job_id,
            "error_url": cancel_url+"?case_id=%s"%job_id,
            "related_id": "aln.job,%s"%job_id,
        }
        res=meth.start_payment(context=ctx)
        pmt_url=res["payment_action"]["url"]
        return {
            "case_id": job_id,
            "payment_url": pmt_url,
        }

    def get_case_info(self,case_id,context={}):
        if not case_id:
            raise Exception("Missing case_id")
        obj=get_model("aln.job").browse(case_id)
        data={
            "case_id": obj.id,
            "client_id": obj.client_id.id,
            "client_name": obj.client_id.name,
            "client_email": obj.client_id.email,
            "lawyer_id": obj.lawyer_id.id,
            "lawyer_name": obj.lawyer_id.name,
            "parties": obj.parties,
            "facts": obj.facts,
            "questions": obj.questions,
            "qc_status": obj.qc_state,
            "call_times": json.loads(obj.call_times) if obj.call_times else None,
            "qc_call_time": obj.qc_call_time,
            "categ_id": obj.qc_categ_id.id,
            "categ_name": obj.qc_categ_id.name if obj.qc_categ_id else None,
            "case_number": obj.number,
        }
        return data

    def get_cases(self,lawyer_id=None,client_id=None,context={}):
        cond=[]
        if lawyer_id:
            cond.append(["lawyer_id","=",lawyer_id])
        if client_id:
            cond.append(["client_id","=",client_id])
        data=[]
        for obj in get_model("aln.job").search_browse(cond):
            vals={
                "case_id": obj.id,
                "client_id": obj.client_id.id,
                "client_name": obj.client_id.name,
                "client_email": obj.client_id.email,
                "lawyer_id": obj.lawyer_id.id,
                "lawyer_name": obj.lawyer_id.name,
                "parties": obj.parties,
                "facts": obj.facts,
                "questions": obj.questions,
                "qc_status": obj.qc_state,
                "call_times": json.loads(obj.call_times) if obj.call_times else None,
                "qc_call_time": obj.qc_call_time,
                "categ_id": obj.qc_categ_id.id,
                "categ_name": obj.qc_categ_id.name if obj.qc_categ_id else None,
                "case_number": obj.number,
            }
            data.append(vals)
        return data

    def qc_accept_case(self,case_id,context={}):
        job=get_model("aln.job").browse(case_id)
        job.write({"qc_state":"wait_confirm_time"})
        job.trigger("qc_accepted")

    def qc_decline_case(self,case_id,reason_id,context={}):
        if not reason_id:
            raise Exception("Missing reason_id")
        job=get_model("aln.job").browse(case_id)
        job.write({"qc_state":"declined","decline_reason_id":reason_id})
        job.trigger("qc_declined")

    def qc_get_decline_reasons(self,context={}):
        data=[]
        for obj in get_model("reason.code").search_browse([["type","=","qc_decline"]]):
            data.append({
                "reason_id": obj.id,
                "title": obj.name,
            })
        return data

    def qc_confirm_call_time(self,case_id,call_time,context={}):
        job=get_model("aln.job").browse(case_id)
        job.write({"qc_state":"ready_call","qc_call_time":call_time})
        job.trigger("qc_time_confirmed")

    def qc_start_call(self,case_id,record_call=False,context={}):
        job=get_model("aln.job").browse(case_id)
        if not job.client_id.phone:
            raise Exception("Missing client phone")
        if not job.lawyer_id.phone:
            raise Exception("Missing lawyer phone")
        vals={
            "phone_from": job.client_id.phone,
            "phone_to": job.lawyer_id.qc_phone or job.lawyer_id.phone,
            "plan_time": job.qc_call_time,
            "related_id": "aln.job,%s"%job.id,
        }
        call_id=get_model("voice.call").create(vals)
        call=get_model("voice.call").browse(call_id)
        call.start_call()
        return {
            "call_id": call_id,
        }

    def qc_get_call_status(self,call_id,context={}):
        call=get_model("voice.call").browse(call_id)
        return {
            "call_id": call_id,
            "call_status": call.state,
        }

    def qc_change_phone(self,lawyer_id,phone,context={}):
        lawyer=get_model("aln.lawyer").browse(lawyer_id)
        lawyer.write({"qc_phone":phone})

API.register()
