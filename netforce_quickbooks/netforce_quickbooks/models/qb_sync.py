from netforce.model import Model,fields,get_model
from netforce import utils
from netforce import tasks
import csv
from decimal import *

def fmt_date(s):
    if not s:
        return None
    try:
        res=s.split("/")
        return res[2]+"-"+res[1]+"-"+res[0]
    except:
        raise Exception("Invalid date: %s"%s)

class Sync(Model):
    _name="qb.sync"
    _fields={
        "file": fields.File("CSV File",required=True),
    }

    def do_import(self,ids,context={}):
        obj=self.browse(ids[0])
        if not obj.file:
            raise Exception("File is missing")
        job_id=context.get("job_id")
        path=utils.get_file_path(obj.file)
        f=open(path,encoding='utf-8', errors='ignore')
        rd=csv.reader(f)
        purch_ids=[]
        old_purch_ids = set()
        for i,line in enumerate(rd):
            if i==0:
                continue
            print("line",line)
            type=line[1]
            if not type:
                continue
            date=fmt_date(line[2])
            memo=line[3]
            deliv_date=fmt_date(line[4])
            num=line[5]
            source=line[6]
            item=line[7]
            qty=line[8]
            recd=line[9] 
            uom=line[10]
            price=Decimal(line[11] or 0)
            amt=line[12]
            bal=line[13]
            prod_code=line[14]
            #item=line[15] # Add "item" excel column as product categ
            if prod_code in ("S","SP"):
                continue
            require_lot=True # XXX Max 13 Dec 2021: True by default since all new items need serial number
            if line[15].upper()=="FALSE":
                require_lot=False    
            cont_vals={
                "supplier": True,
                "name": source,
            }
            res=get_model("contact").search([["name","=",source]])
            if res:
                cont_id=res[0]
            else:
                cont_id=get_model("contact").create(cont_vals)
            if num.find("-")!=-1:
                proj_no=num.split("-")[0].strip()
                res=get_model("project").search([["name","=",proj_no]])
                if not res:
                    raise Exception("Project not found: %s"%proj_no)
                proj_id=res[0]
            else:
                proj_id=None
            po_vals={
                "number": num,
                "date": date,
                "date_required": deliv_date,
                "contact_id": cont_id,
                "ref": "Quickbooks import",
                "project_id": proj_id,
            }
            res=get_model("purchase.order").search([["number","=",num]])
            if res:
                purch_id=res[0]
                if purch_id not in purch_ids:
                    raise Exception("Purchase Order %s already exist. Please delete the PO and any related transactions if you wish to reimport." % num)
            else:
                purch_id=get_model("purchase.order").create(po_vals)
                purch_ids.append(purch_id)
            uom_vals={
                "name": uom,
            }
            res=get_model("uom").search([["name","=",uom]])
            if res:
                uom_id=res[0]
            else:
                uom_id=get_model("uom").create(uom_vals)
            
            prod_categ=get_model("product.categ").search([["name","=",item.upper()]]) # Max 30 Dec 2021
            if prod_categ:
                prod_categ_id=prod_categ[0]
            else:
                prod_categ_id=get_model("product.categ").create({"name":item.upper()})

            prod_name=memo.split(":")[0]
            try:
                prod_desc=memo.split(":")[1]
            except:
                prod_desc="/"

            default_loc=get_model("stock.location").search([["name","=","Warehouse"]]) # Max 14 Dec 2021
            try:
                loc_id=default_loc[0]
            except:
                loc_id=None

            if prod_code:
                prod_vals={
                    "code": prod_code,
                    "name": prod_name,
                    "description": prod_desc,
                    "type": "stock",
                    "uom_id": uom_id,
                    "require_lot": require_lot, # Max 05 Dec 2021
                    "categ_id": prod_categ_id, # Max 30 Dec 2021
                }

                if require_lot: # Max 13 Dec 2021
                    prod_vals.update({"cost_method":"lot"})
                else:
                    prod_vals.update({"cost_method":"fifo"})

                res=get_model("product").search([["code","=",prod_code]])
                if res:
                    prod_id=res[0]
                    prod_loc=get_model("product.location").search_browse([["product_id","=",prod_id]]) # Max 14 Dec 2021
                    if not prod_loc:
                        raise Exception("Missing location for product %s"%prod_code)
                    loc_id=prod_loc[0].location_id.id
                else:
                    prod_id=get_model("product").create(prod_vals)
                    prod_loc_vals={ # Max 14 Dec 2021
                        "product_id": prod_id,
                        "location_id": loc_id,    
                    }
                    get_model("product.location").create(prod_loc_vals)
            else:
                prod_id=None

            if price>=0:
                line_vals={
                    "order_id": purch_id,
                    "description": memo,
                    "product_id": prod_id,
                    "uom_id": uom_id,
                    "qty": qty,
                    "unit_price": price,
                    "location_id": loc_id,
                }
                print("line_vals",line_vals)
                #res=get_model("purchase.order.line").search([["order_id","=",purch_id],["description","=",memo]])
                #if not res:
                    #get_model("purchase.order.line").create(line_vals)
                get_model("purchase.order.line").create(line_vals)
            #elif prod_id:
                #res=get_model("purchase.order.line").search([["order_id","=",purch_id],["product_id","=",prod_id]])
                #if not res:
                #    raise Exception("Product not found in PO: %s %s"%(prod_id,purch_id))
                #line_id=res[0]
                #line_vals={
                #    "discount_amount": -price,
                #}
                #get_model("purchase.order.line").write([line_id],line_vals)
        for purch_id in purch_ids:
            print("purch_id",purch_id)
            get_model("purchase.order").exec_func_custom("copy_to_gr_custom",[[purch_id]],{})
        #get_model("purchase.order").exec_func_custom("copy_to_gr_custom",[purch_ids],{})

Sync.register()
