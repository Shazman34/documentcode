# -*- coding: utf-8 -*-
from netforce.model import Model,fields,get_model
from netforce import utils
from netforce import tasks
import dbf
from decimal import *

class Sync(Model):
    _name="xp.sync"
    _fields={
        "import_type": fields.Selection([["product","STMAS.DBF (products)"],["customer","ARMAS.DBF (customers)"],["supplier","APMAS.DBF (suppliers)"],["account","GLACC.DBF (accounts)"],["arship","ARSHIP.DBF (customer shipping addresses"],["acc_set","ISACC.DBF (account sets)"],["st_grp","STCRD.DBF (stock groups)"],["istab","ISTAB.DBF (contact types)"],["famas","FAMAS.DBF (fixed asset)"]],"Import Type"),
        "file": fields.File("DBF File"),
    }

    def merge_uom(self,vals,context={}):
        res=get_model("uom").search([["name","=",vals["name"]]])
        if res:
            uom_id=res[0]
            get_model("uom").write([uom_id],vals)
        else:
            uom_id=get_model("uom").create(vals)
        return uom_id

    def merge_product(self,vals,context={}):
        res=get_model("product").search([["code","=",vals["code"]]])
        if res:
            prod_id=res[0]
            get_model("product").write([prod_id],vals)
        else:
            prod_id=get_model("product").create(vals)
        return prod_id

    def merge_contact(self,vals,context={}):
        res=get_model("contact").search([["code","=",vals["code"]]])
        if res:
            contact_id=res[0]
            get_model("contact").write([contact_id],vals)
        else:
            contact_id=get_model("contact").create(vals)
        return contact_id

    def merge_account(self,vals,context={}):
        res=get_model("account.account").search([["code","=",vals["code"]]])
        if res:
            account_id=res[0]
            get_model("account.account").write([account_id],vals)
        else:
            account_id=get_model("account.account").create(vals)
        return account_id

    def merge_address(self,vals,context={}):
        res=get_model("address").search([["contact_id","=",vals["contact_id"]],["address","=",vals["address"]],["type","=",vals["type"]]])
        if res:
            addr_id=res[0]
            get_model("address").write([addr_id],vals)
        else:
            addr_id=get_model("address").create(vals)
        return addr_id

    def merge_contact_categ(self,vals,context={}):
        res=get_model("contact.categ").search([["code","=",vals["code"]]])
        if res:
            rec_id=res[0]
            get_model("contact.categ").write([rec_id],vals)
        else:
            rec_id=get_model("contact.categ").create(vals)
        return rec_id

    def merge_prod_categ(self,vals,context={}):
        res=get_model("product.categ").search([["code","=",vals["code"]]])
        if res:
            rec_id=res[0]
            get_model("product.categ").write([rec_id],vals)
        else:
            rec_id=get_model("product.categ").create(vals)
        return rec_id

    def merge_ship_method(self,vals,context={}):
        res=get_model("ship.method").search([["code","=",vals["code"]]])
        if res:
            rec_id=res[0]
            get_model("ship.method").write([rec_id],vals)
        else:
            rec_id=get_model("ship.method").create(vals)
        return rec_id

    def merge_product_categ(self,vals,context={}):
        res=get_model("product.categ").search([["code","=",vals["code"]]])
        if res:
            rec_id=res[0]
            get_model("product.categ").write([rec_id],vals)
        else:
            rec_id=get_model("product.categ").create(vals)
        return rec_id

    def merge_fixed_asset(self,vals,context={}):
        res=get_model("account.fixed.asset").search([["number","=",vals["number"]]])
        if res:
            rec_id=res[0]
            get_model("account.fixed.asset").write([rec_id],vals)
        else:
            rec_id=get_model("account.fixed.asset").create(vals)
        return rec_id

    def do_import(self,ids,context={}):
        obj=self.browse(ids[0])
        job_id=context.get("job_id")
        if obj.import_type=="product":
            path=utils.get_file_path(obj.file)
            d=dbf.Table(path)
            d.open()
            res=get_model("price.list").search([["code","=","1"]])
            if not res:
                raise Exception("Pricelist #1 not found")
            pricelist1_id=res[0]
            res=get_model("price.list").search([["code","=","2"]])
            if not res:
                raise Exception("Pricelist #2 not found")
            pricelist2_id=res[0]
            for i,r in enumerate(d):
                if job_id:
                    if tasks.is_aborted(job_id):
                        return
                    tasks.set_progress(job_id,i*100/len(d),"Importing product %s of %s."%(i+1,len(d)))
                code=r["stkcod"].strip()
                #if code!="8853963007782":
                #    continue
                name_th=r["stkdes"].strip()
                name_en=r["stkdes2"].strip()
                barcode=r["barcod"].strip()
                categ_code=r["stkgrp"].strip()
                res=get_model("product.categ").search([["code","=",categ_code]])
                if res:
                    categ_id=res[0]
                else:
                    categ_id=get_model("product.categ").create({"name":categ_code,"code":categ_code})
                uom=r["qucod"].strip()
                uom_id=self.merge_uom({"name":uom,"type":"unit"})
                sale_price1=r["sellpr1"]
                sale_price2=r["sellpr2"]
                purch_price=r["lpurpr"]
                print("record",r)
                vals={
                    "code":code,
                    "name": {
                        "en_US": name_en,
                        "th_TH": name_th,
                    },
                    "type":"stock",
                    "uom_id":uom_id,
                    "barcode": barcode,
                    "description":"",
                    "categ_id": categ_id,
                    "sale_price":sale_price1,
                    "purchase_price":purch_price,
                    "pricelist_items": [("delete_all",)],
                }
                price_vals={
                    "list_id": pricelist1_id,
                    "price": sale_price1,
                }
                vals["pricelist_items"].append(("create",price_vals))
                price_vals={
                    "list_id": pricelist2_id,
                    "price": sale_price2,
                }
                vals["pricelist_items"].append(("create",price_vals))
                self.merge_product(vals)
        elif obj.import_type=="customer":
            path=utils.get_file_path(obj.file)
            d=dbf.Table(path)
            d.open()
            for i,r in enumerate(d):
                if job_id:
                    if tasks.is_aborted(job_id):
                        return
                    tasks.set_progress(job_id,i*100/len(d),"Importing customer %s of %s."%(i+1,len(d)))
                print("record",r)
                categ_code=r["custyp"].strip()
                if categ_code:
                    res=get_model("contact.categ").search([["code","=",categ_code]])
                    if not res:
                        raise Exception("Contact category code not found: '%s'"%categ_code)
                    categ_id=res[0]
                else:
                    categ_id=None
                code=r["cuscod"].strip()
                name=r["cusnam"].strip()
                prenam=r["prenam"].strip()
                if code.startswith("C-") or code.startswith("CDS"): # XXX
                    cont_type="person"
                else:
                    cont_type="org"
                addr1=r["addr01"].strip()
                addr2=r["addr02"].strip()
                addr3=r["addr03"].strip()
                postal_code=r["zipcod"].strip().replace(".0","")
                phone=r["telnum"].strip()
                contact=r["contact"].strip()
                tax_no=r["taxid"]
                tax_branch_no=str(r["orgnum"])
                addr_vals={
                    "type": "billing",
                    "address": addr1,
                    "address2": addr2+addr3,
                    "postal_code": postal_code,
                }
                addrs=[("delete_all",),("create",addr_vals)]
                if r["status"]=="A":
                    state="active"
                else:
                    state="inactive"
                acc_code=r["accnum"].strip()
                if acc_code:
                    res=get_model("account.account").search([["code","=",acc_code]])
                    if not res:
                        raise Exception("Account not found: %s"%acc_code)
                    acc_id=res[0]
                else:
                    acc_id=None
                ship_method_id=None
                pay_method_id=None
                dlvby=r["dlvby"].strip()
                if dlvby:
                    res=get_model("ship.method").search([["code","=",dlvby]])
                    if not res:
                        raise Exception("Shipping method code not found: %s"%divby)
                    ship_method_id=res[0]
                paycond=r["paycond"].strip()
                if paycond:
                    res=get_model("payment.method").search([["code","=",paycond]])
                    if res:
                        pay_method_id=res[0]
                    else:
                        pay_method_id=get_model("payment.method").create({"name":paycond,"code":paycond})
                paytrm=r["paytrm"] or 0
                crline=r["crline"] or 0
                disc=float(r["disc"].strip().replace("%","") or 0) # XXX
                vals={
                    "code": code,
                    "type": cont_type,
                    "title": prenam,
                    "customer": True,
                    "phone": phone,
                    "tax_no": tax_no,
                    "tax_branch_no": tax_branch_no,
                    "addresses": addrs,
                    "state": state,
                    "account_receivable_id": acc_id,
                    "sale_pay_method_id": pay_method_id,
                    "ship_method_id": ship_method_id,
                    "sale_discount": disc,
                    "sale_pay_term_days": paytrm,
                    "sale_max_credit": crline,
                    "categ_id": categ_id,
                }
                if cont_type=="person":
                    name=name.replace("\xa0"," ")
                    res=name.split(" ")
                    first_name=res[0]
                    last_name=" ".join(res[1:]).strip() or "/"
                    vals["first_name"]=first_name
                    vals["last_name"]=last_name
                else:
                    vals["name"]=name
                self.merge_contact(vals)
        elif obj.import_type=="supplier":
            path=utils.get_file_path(obj.file)
            d=dbf.Table(path)
            d.open()
            for i,r in enumerate(d):
                if job_id:
                    if tasks.is_aborted(job_id):
                        return
                    tasks.set_progress(job_id,i*100/len(d),"Importing supplier %s of %s."%(i+1,len(d)))
                print("record",r)
                code=r["supcod"].strip()
                name=r["supnam"].strip()
                addr1=r["addr01"]
                addr2=r["addr02"]
                postal_code=r["zipcod"].strip().replace(".0","")
                phone=r["telnum"]
                tax_no=r["taxid"]
                addr_vals={
                    "type": "billing",
                    "address": addr1,
                    "address2": addr2,
                    "postal_code": postal_code,
                }
                addrs=[("delete_all",),("create",addr_vals)]
                self.merge_contact({"code":code,"name":name,"supplier":True,"phone":phone,"tax_no":tax_no,"addresses":addrs})
        elif obj.import_type=="account":
            path=utils.get_file_path(obj.file)
            d=dbf.Table(path)
            d.open()
            for i,r in enumerate(d):
                print("record",r)
                if job_id:
                    if tasks.is_aborted(job_id):
                        return
                    tasks.set_progress(job_id,i*100/len(d),"Importing account %s of %s."%(i+1,len(d)))
                code=r["accnum"].strip()
                name_th=r["accnam"].strip() or "/" # XXX
                name_en=r["accnam2"].strip() or name_th
                name={
                    "en_US": name_en,
                    "th_TH": name_th,
                }
               # name=(r["accnam2"] or r["accnam"]).strip() or "/" # XXX
                parent=r["parent"].strip()
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
                #if 0:
                if parent:
                    res=get_model("account.account").search([["code","=",parent]])
                    if not res:
                        raise Exception("Parent not found: %s"%parent)
                    parent_id=res[0]
                    self.merge_account({"code":parent,"type":"view"})
                else:
                    parent_id=None
                self.merge_account({"code":code,"name":name,"type":type,"parent_id":parent_id})
        elif obj.import_type=="arship":
            path=utils.get_file_path(obj.file)
            d=dbf.Table(path)
            d.open()
            for i,r in enumerate(d):
                if job_id:
                    if tasks.is_aborted(job_id):
                        return
                    tasks.set_progress(job_id,i*100/len(d),"Importing address %s of %s."%(i+1,len(d)))
                print("record",r)
                cuscod=r["cuscod"].strip()
                res=get_model("contact").search([["code","=",cuscod]])
                if not res:
                    #raise Exception("Customer code not found: %s"%cuscod)
                    print("WARNING: Customer code not found: %s"%cuscod)
                    continue
                contact_id=res[0]
                addr01=r["addr01"].strip()
                addr02=r["addr02"].strip()
                addr03=r["addr03"].strip()
                zipcod=r["zipcod"].strip()
                telnum=r["telnum"].strip()
                contact=r["contact"].strip()
                vals={
                    "type": "shipping",
                    "contact_id": contact_id,
                    "address": addr01,
                    "address2": addr02+addr03,
                    "postal_code": zipcod,
                    "phone": telnum,
                    "contact_name": contact,
                }
                self.merge_address(vals)
        elif obj.import_type=="istab":
            path=utils.get_file_path(obj.file)
            d=dbf.Table(path)
            d.open()
            for i,r in enumerate(d):
                if job_id:
                    if tasks.is_aborted(job_id):
                        return
                    tasks.set_progress(job_id,i*100/len(d),"importing record %s of %s."%(i+1,len(d)))
                print("record",r)
                tabtyp=r["tabtyp"].strip()
                code=r["typcod"].strip()
                name_th=r["shortnam"].strip()
                name_en=r["shortnam2"].strip()
                desc_th=r["typdes"].strip()
                desc_en=r["typdes2"].strip()
                vals={
                    "code": code,
                    "name": {
                        "en_US": name_en,
                        "th_TH": name_th,
                    },
                    "description": {
                        "en_US": desc_en,
                        "th_TH": desc_th,
                    },
                }
                if tabtyp=="45":
                    self.merge_contact_categ(vals)
                elif tabtyp=="41":
                    self.merge_ship_method(vals)
                elif tabtyp=="22":
                    self.merge_prod_categ(vals)
        elif obj.import_type=="acc_set":
            path=utils.get_file_path(obj.file)
            d=dbf.Table(path)
            d.open()
            for i,r in enumerate(d):
                if job_id:
                    if tasks.is_aborted(job_id):
                        return
                    tasks.set_progress(job_id,i*100/len(d),"importing record %s of %s."%(i+1,len(d)))
                print("record",r)
        elif obj.import_type=="st_grp":
            path=utils.get_file_path(obj.file)
            d=dbf.Table(path)
            d.open()
            for i,r in enumerate(d):
                if job_id:
                    if tasks.is_aborted(job_id):
                        return
                    tasks.set_progress(job_id,i*100/len(d),"importing record %s of %s."%(i+1,len(d)))
                print("record",r)
        elif obj.import_type=="famas":
            path=utils.get_file_path(obj.file)
            d=dbf.Table(path)
            d.open()
            for i,r in enumerate(d):
                if job_id:
                    if tasks.is_aborted(job_id):
                        return
                    tasks.set_progress(job_id,i*100/len(d),"importing record %s of %s."%(i+1,len(d)))
                print("record",r)
                code=r["fascod"]
                desc_th=r["fasdes"]
                desc_en=r["fasdes2"]
                serial=r["serial"]
                life=r["life"]
                rate=r["rate"]
                salvage=r["salval"]
                purch_price=r["cosval"]
                type_code=r["fasgrp"].strip()
                if type_code:
                    res=get_model("account.fixed.asset.type").search([["code","=",type_code]])
                    if res:
                        type_id=res[0]
                    else:
                        type_id=get_model("account.fixed.asset.type").create({"name":type_code,"code":type_code})
                vals={
                    "number": code,
                    "name": {
                        "en_US": desc_en,
                        "th_TH": desc_th,
                    },
                    "dep_rate": rate,
                    "price_purchase": purch_price,
                }
                self.merge_fixed_asset(vals)
        else:
            raise Exception("Invalid import type")

Sync.register()
