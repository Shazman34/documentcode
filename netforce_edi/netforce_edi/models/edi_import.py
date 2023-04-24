from netforce.model import Model,fields,get_model
from netforce import utils
from netforce import tasks
import csv
from decimal import *
import zipfile
from lxml import etree
import xlrd
from datetime import *
import time
from io import StringIO
from dateutil.relativedelta import relativedelta
import codecs
from pprint import pprint


def get_col_no(name):
    return ord(name)-ord("A")

class Import(Model):
    _name="edi.import"
    _fields={
        "import_type": fields.Selection([["thaisupplynet","ThaiSupplyNet (CSV)"],["aic","AIC.co.th"],["7_eleven","7-Eleven (CSV)"],["bigc","BigC (CSV)"],["jusco","Jusco (CSV)"],["tops","Tops (CSV)"],["tesco","Tesco (XML ZIP)"],["talaypu","Talaypu (XLS)"],["7_eleven_zip","7-Eleven (ZIP)"],["bigc_zip","BigC (ZIP)"],["jusco_zip","Jusco (ZIP)"],["tops_zip","Tops (ZIP)"],["sellsuki","Sellsuki (XLS)"],["kff_bom","KFF BoM (XLS)"],["talaypu_sale_forecast","Talaypu Sales Forecast (XLS)"]],"Import Type",required=True),
        "file": fields.File("Import File"),
        "password": fields.Char("Password"),
        "customer_id": fields.Many2One("contact","Customer"),
    }

    def do_import(self,ids,context={}):
        obj=self.browse(ids[0])
        path=utils.get_file_path(obj.file)
        job_id=context.get("job_id")
        if obj.import_type=="thaisupplynet":
            #f=codecs.open(path,encoding="utf-8",errors="ignore")
            f=codecs.open(path,encoding="utf-16",errors="ignore")
            rd = csv.reader(f)
            headers = next(rd)
            headers = [h.strip() for h in headers]
            order_rows={}
            for i,row in enumerate(rd):
                print("row #%s"%i)
                order_no=row[0]
                order_rows.setdefault(order_no,[]).append(row)
            for order_no,rows in order_rows.items():
                if not obj.customer_id:
                    raise Exception("Missing customer")
                date_s=rows[0][3]
                date=date_s[6:]+"-"+date_s[3:5]+"-"+date_s[0:2]
                order_vals={
                    "contact_id": obj.customer_id.id,
                    "number": order_no,
                    "date": date,
                    "lines": [("delete_all",)],
                }
                for row in rows:
                    seq=row[9]
                    barcode=row[10].strip()
                    code=row[11].strip()
                    desc=row[12].strip()
                    qty=Decimal(row[14].replace(",",""))
                    amt=Decimal(row[15].replace(",",""))
                    price=amt/qty
                    res=get_model("product").search(["or",["code","=",code],["barcode","=",barcode],["customers.customer_product_code","=",code]])
                    if not res:
                        raise Exception("Product not found: %s"%code)
                    prod_id=res[0]
                    prod=get_model("product").browse(prod_id)
                    line_vals={
                        "sequence": seq,
                        "product_id": prod_id,
                        "description": desc,
                        "qty": qty,
                        "uom_id": prod.uom_id.id,
                        "unit_price": price,
                    }
                    order_vals["lines"].append(("create",line_vals))
                print("order_vals")
                pprint(order_vals)
                res=get_model("sale.order").search([["number","=",order_no]])
                if res:
                    order_id=res[0]
                    get_model("sale.order").write([order_id],order_vals)
                else:
                    get_model("sale.order").create(order_vals)
        elif obj.import_type in ("7_eleven","bigc","jusco","tops"):
            buf=open(path,"rb").read()
            data=buf.decode("tis-620")
            lines=data.split("\n")
            res=lines[1].split("|")[0].split()[1]
            order_date=res[:4]+"-"+res[4:6]+"-"+res[6:8]
            print("order_date",order_date)
            prods=lines[3].split("|")[2:-1]
            prod_ids=[]
            for prod in prods:
                code=prod.split(" ")[0]
                print("code",code)
                res=get_model("product").search([["code","=",code]])
                if not res:
                    res=get_model("product").search([["customers.customer_product_code","=",code]])
                    if not res:
                        raise Exception("Product code not found: %s"%code)
                prod_id=res[0]
                prod_ids.append(prod_id)
            print("prod_ids",prod_ids)
            n=0
            for line in lines[4:]:
                cols=line.split("|")
                num=cols[0].strip()
                if not num:
                    continue
                contact_code=cols[1].split(" ")[0]
                if obj.import_type=="7_eleven":
                    contact_code="7ELEVEN-"+contact_code
                res=get_model("contact").search([["code","=",contact_code]])
                if not res:
                    raise Exception("Contact not found: %s"%contact_code)
                contact_id=res[0]
                res=get_model("sale.order").search([["contact_id","=",contact_id],["date","=",order_date]])
                if res:
                    raise Exception("sales order already created for contact=%s date=%s"%(contact_code,order_date))
                sale_vals={
                    "contact_id": contact_id,
                    "date": order_date,
                    "ref": "FROM EDI",
                    "lines": [],
                }
                seq=0
                for i,col in enumerate(cols[2:-1]):
                    qty=Decimal(col)
                    if qty<=0:
                        continue
                    prod_id=prod_ids[i]
                    prod=get_model("product").browse(prod_id)
                    seq+=1
                    line_vals={
                        "sequence": seq,
                        "product_id": prod_id,
                        "description": prod.name or "/",
                        "qty": qty,
                        "uom_id": prod.uom_id.id,
                        "unit_price": prod.sale_price or 0,
                    }
                    sale_vals["lines"].append(("create",line_vals))
                sale_id=get_model("sale.order").create(sale_vals)
                n+=1
            return {
                "alert": "%d sales orders created"%n,
            }
        elif obj.import_type in ("7_eleven_zip","bigc_zip","jusco_zip","tops_zip"):
            zf=zipfile.ZipFile(path)
            res=zf.namelist()
            if not res:
                raise Exception("Zip file is empty")
            fname=res[0]
            if obj.password:
                buf=zf.read(fname,pwd=obj.password.encode("utf-8"))
            else:
                buf=zf.read(fname)
            f=StringIO(buf.decode("tis-620"))
            rd=csv.reader(f)
            prev_po_num=None
            sale_id=None
            sale_ids=[]
            n=0
            for i,row in enumerate(rd):
                print("row #%s"%i)
                po_num=row[0]
                if not po_num:
                    continue
                order_date=row[1]
                due_date=row[2]
                prod_code=row[26]
                remarks=row[19]
                qty=row[30]
                price=row[33]
                if po_num!=prev_po_num:
                    if not obj.customer_id:
                        raise Exception("Missing customer")
                    sale_vals={
                        "contact_id": obj.customer_id.id,
                        "ref": "FROM EDI (%s)"%po_num,
                        "date": order_date,
                        "due_date": due_date,
                        "delivery_date": due_date,
                        "lines": [],
                    }
                    sale_id=get_model("sale.order").create(sale_vals)
                    sale_ids.append(sale_id)
                    n+=1
                    prev_po_num=po_num
                res=get_model("product").search([["code","=",prod_code]])
                if not res:
                    raise Exception("Product not found: %s"%prod_code)
                prod_id=res[0]
                prod=get_model("product").browse(prod_id)
                line_vals={
                    "order_id": sale_id,
                    "product_id": prod.id,
                    "description": prod.name,
                    "qty": qty,
                    "uom_id": prod.sale_uom_id.id or prod.uom_id.id,
                    "unit_price": price,
                    "tax_id": prod.sale_tax_id,
                }
                get_model("sale.order.line").create(line_vals)
            get_model("sale.order").function_store(sale_ids)
            return {
                "alert": "%d sales orders created"%n,
            }
        elif obj.import_type=="tesco":
            zf=zipfile.ZipFile(path)
            res=zf.namelist()
            if not res:
                raise Exception("Zip file is empty")
            fname=res[0]
            buf=zf.read(fname)
            root=etree.fromstring(buf)
            head=root.find("po_header")
            order_date=head.find("order_date").text
            delivery_date=head.find("delivery_date").text
            contact_code="TESCO"
            res=get_model("contact").search([["code","=",contact_code]])
            if not res:
                raise Exception("Contact code not found: %s"%contact_code)
            contact_id=res[0]
            res=get_model("sale.order").search([["contact_id","=",contact_id],["date","=",order_date]])
            if res:
                raise Exception("sales order already created for contact=%s date=%s"%(contact_code,order_date))
            sale_vals={
                "contact_id": contact_id,
                "date": order_date,
                "delivery_date": delivery_date,
                "ref": "FROM EDI",
                "lines": [],
            }
            for el in root.find("po_items"):
                seq=el.attrib["item_number"]
                sku=el.find("SKU").text
                ean=el.find("EAN").text
                qty=Decimal(el.find("ordered_quantity").text)
                res=get_model("product").search([["code","=",sku]])
                prod_id=res[0] if res else None
                if not prod_id:
                    res=get_model("product").search([["code","=",ean]])
                    prod_id=res[0] if res else None
                    if not prod_id:
                        raise Exception("Product not found: sku=%s ean=%s"%(sku,ean))
                    prod=get_model("product").browse(prod_id)
                line_vals={
                    "sequence": seq,
                    "product_id": prod_id,
                    "description": prod.name or "/",
                    "qty": qty,
                    "uom_id": prod.uom_id.id,
                    "unit_price": prod.sale_price or 0,
                }
                sale_vals["lines"].append(("create",line_vals))
            if not sale_vals["lines"]:
                raise Exception("Order is empty")
            sale_id=get_model("sale.order").create(sale_vals)
            return {
                "alert": "%d product codes ordered"%len(sale_vals["lines"]),
            }
        elif obj.import_type=="talaypu":
            book=xlrd.open_workbook(path)
            sheet=book.sheet_by_index(0)
            contact_code=sheet.cell(1,get_col_no("K")).value.strip()
            print("contact_code",contact_code)
            if not contact_code:
                raise Exception("Missing contact code (cell K2)")
            res=get_model("contact").search([["code","=",contact_code]])
            if not res:
                raise Exception("Contact code not found: %s"%contact_code)
            contact_id=res[0]
            val=sheet.cell(3,get_col_no("K")).value
            if not val:
                raise Exception("Missing order date (cell K4)")
            d = datetime(*xlrd.xldate_as_tuple(val, book.datemode))
            order_date=d.strftime("%Y-%m-%d")
            print("order_date",order_date)
            res=get_model("sale.order").search([["contact_id","=",contact_id],["date","=",order_date]])
            if res:
                raise Exception("sales order already created for contact=%s date=%s"%(contact_code,order_date))
            sale_vals={
                "contact_id": contact_id,
                "date": order_date,
                "ref": "FROM EDI",
                "lines": [],
            }
            for row_no in range(6,sheet.nrows-1):
                val=sheet.cell(row_no,get_col_no("F")).value
                if not val:
                    continue
                prod_code=str(int(val))
                qty=sheet.cell(row_no,get_col_no("S")).value
                if not qty:
                    continue
                price=sheet.cell(row_no,get_col_no("K")).value
                disc_price=sheet.cell(row_no,get_col_no("M")).value
                res=get_model("product").search([["code","=",prod_code]])
                if not res:
                    raise Exception("Product code not found: %s"%prod_code)
                prod_id=res[0]
                prod=get_model("product").browse(prod_id)
                line_vals={
                    "product_id": prod_id,
                    "description": prod.name or "/",
                    "qty": qty,
                    "uom_id": prod.uom_id.id,
                    "unit_price": disc_price or price,
                }
                sale_vals["lines"].append(("create",line_vals))
            if not sale_vals["lines"]:
                raise Exception("Order is empty")
            sale_id=get_model("sale.order").create(sale_vals)
            return {
                "alert": "%d product codes ordered"%len(sale_vals["lines"]),
            }
        elif obj.import_type=="sellsuki":
            # XXX: comment exeption in xlrd code to avoid error
            # TODO: where get contact
            book=xlrd.open_workbook(path)
            sheet=book.sheet_by_index(0)
            prev_order_no=None
            sale_ids=[]
            res=get_model("contact.categ").search([["code","=","SELLSUKI"]])
            if not res:
                raise Exception("Contact category not found")
            categ_id=res[0]
            categ=get_model("contact.categ").browse(categ_id)
            for row_no in range(1,sheet.nrows-1):
                if job_id:
                    if tasks.is_aborted(job_id):
                        return
                    tasks.set_progress(job_id,row_no*100/sheet.nrows,"Importing record %s of %s."%(row_no,sheet.nrows))
                order_no=sheet.cell(row_no,get_col_no("X")).value
                if not order_no:
                    continue
                val=sheet.cell(row_no,get_col_no("B")).value
                if not val:
                    raise Exception("Missing order date")
                d=datetime.strptime(val,"%d/%m/%Y")
                order_date=d.strftime("%Y-%m-%d")
                if order_no!=prev_order_no:
                    name=sheet.cell(row_no,get_col_no("F")).value
                    addr=sheet.cell(row_no,get_col_no("G")).value
                    city=sheet.cell(row_no,get_col_no("H")).value
                    postal_code=sheet.cell(row_no,get_col_no("I")).value
                    email=sheet.cell(row_no,get_col_no("K")).value
                    phone=sheet.cell(row_no,get_col_no("L")).value
                    channel=sheet.cell(row_no,get_col_no("N")).value
                    res=get_model("contact").search([["name","=",name],["categ_id","=",categ_id]])
                    if res:
                        contact_id=res[0]
                    else:
                        vals={
                            "last_name": name or "/",
                            "email": email,
                            "phone": phone,
                            "customer": True,
                            "categ_id": categ_id,
                        }
                        contact_id=get_model("contact").create(vals)
                    res=get_model("address").search([["address","=",addr],["contact_id","=",contact_id]])
                    if res:
                        addr_id=res[0]
                    else:
                        vals={
                            "contact_id": contact_id,
                            "address": addr,
                            "postal_code": postal_code,
                        }
                        addr_id=get_model("address").create(vals)
                    chan_id=None
                    if channel:
                        res=get_model("sale.channel").search([["name","=",channel]])
                        if res:
                            chan_id=res[0]
                        else:
                            vals={
                                "name": channel,
                            }
                            chan_id=get_model("sale.channel").create(vals)
                    vals={
                        "contact_id": contact_id,
                        "date": order_date,
                        "ref": "EDI SellSuki: %s"%order_no,
                        "sale_channel_id": chan_id,
                        "bill_address_id": addr_id,
                        "ship_address_id": addr_id,
                    }
                    res=get_model("sale.order").search([["ref","=",vals["ref"]]])
                    if res:
                        sale_id=res[0]
                        vals["lines"]=[("delete_all",)]
                        get_model("sale.order").write([sale_id],vals)
                    else:
                        sale_id=get_model("sale.order").create(vals)
                    sale_ids.append(sale_id)
                prod_code=str(sheet.cell(row_no,get_col_no("R")).value).replace(".0","")
                res=get_model("product").search([["code","=",prod_code]])
                if not res:
                    raise Exception("Product code not found: %s"%prod_code)
                prod_id=res[0]
                prod=get_model("product").browse(prod_id)
                qty=int(sheet.cell(row_no,get_col_no("S")).value)
                price=float(sheet.cell(row_no,get_col_no("T")).value)
                vals={
                    "order_id": sale_id,
                    "product_id": prod.id,
                    "description": prod.name,
                    "qty": qty,
                    "uom_id": prod.uom_id.id,
                    "unit_price": price,
                }
                get_model("sale.order.line").create(vals)
            for sale in get_model("sale.order").browse(sale_ids):
                sale.to_draft()
                sale.confirm()
            return {
                "alert": "%d sales orders imported"%len(sale_ids),
            }
        elif obj.import_type=="kff_bom":
            book=xlrd.open_workbook(path)
            sheet=book.sheet_by_index(0)
            bom_ids=[]
            bom_id=None
            for row_no in range(1,sheet.nrows-1):
                prod_code=sheet.cell(row_no,get_col_no("C")).value
                if not prod_code:
                    continue
                prod_name=sheet.cell(row_no,get_col_no("D")).value
                qty=sheet.cell(row_no,get_col_no("E")).value
                uom_name=sheet.cell(row_no,get_col_no("F")).value
                uom_id=self.import_uom(uom_name)
                prod_id=self.import_product(prod_code,prod_name,uom_id)
                bom_no=sheet.cell(row_no,get_col_no("A")).value
                if bom_no:
                    vals={
                        "number": "IMPORT-%.3d"%int(bom_no),
                        "product_id": prod_id,
                        "qty": 1,
                        "uom_id": uom_id,
                        "lines": [("delete_all",)],
                    }
                    res=get_model("bom").search([["number","=",vals["number"]]])
                    if res:
                        bom_id=res[0]
                        get_model("bom").write([bom_id],vals)
                    else:
                        bom_id=get_model("bom").create(vals)
                    bom_ids.append(bom_id)
                else:
                    vals={
                        "bom_id": bom_id,
                        "product_id": prod_id,
                        "uom_id": uom_id,
                        "qty": qty,
                    }
                    get_model("bom.line").create(vals)
            return {
                "alert": "%d BoMs imported"%len(bom_ids),
            }
        elif obj.import_type=="talaypu_sale_forecast":
            book=xlrd.open_workbook(path)
            sheet_names=book.sheet_names()
            n=0
            miss_custs=[]
            miss_prods=[]
            for sheet_no in range(book.nsheets):
                sheet=book.sheet_by_index(sheet_no)
                cust_code=sheet_names[sheet_no]
                res=get_model("contact").search([["code","=",cust_code]])
                if not res:
                    print("WARNING: customer code not found: %s"%cust_code)
                    miss_custs.append(cust_code)
                    continue
                contact_id=res[0]
                col_months={}
                for col_no in range(0,sheet.ncols):
                    val=sheet.cell(3,col_no).value
                    if not val:
                        continue
                    try:
                        d = datetime(*xlrd.xldate_as_tuple(val, book.datemode))
                        month=d.strftime("%Y-%m")
                        col_months[col_no]=month
                    except:
                        pass
                print("col_months",col_months)
                for row_no in range(5,sheet.nrows-1):
                    code=sheet.cell(row_no,get_col_no("A")).value
                    if not code:
                        continue
                    if isinstance(code,float): # XXX
                        code=str(int(code))
                    res=get_model("product").search([["code","=",code]])
                    if not res:
                        miss_prods.append(code)
                        continue
                    prod_id=res[0]
                    prod=get_model("product").browse(prod_id)
                    if job_id:
                        if tasks.is_aborted(job_id):
                            return
                        tasks.set_progress(job_id,row_no*100/sheet.nrows,"Importing forecasts for product %s (%s of %s)."%(code,row_no,sheet.nrows))
                    for col_no in range(0,sheet.ncols):
                        month=col_months.get(col_no)
                        if not month:
                            continue
                        val=sheet.cell(row_no,col_no).value
                        if not val:
                            continue
                        qty=int(val)
                        name="SF-IMPORT-"+month
                        res=get_model("sale.forecast").search([["number","=",name]])
                        if res:
                            sf_id=res[0]
                        else:
                            vals={
                                "number": name,
                                "date_from": month+"-01",
                                "date_to": (datetime.strptime(month+"-01","%Y-%m-%d")+relativedelta(day=31)).strftime("%Y-%m-%d"),
                            }
                            sf_id=get_model("sale.forecast").create(vals)
                        res=get_model("sale.forecast.line").search([["forecast_id","=",sf_id],["product_id","=",prod_id],["customer_id","=",contact_id]])
                        if res:
                            line_id=res[0]
                            get_model("sale.forecast.line").write([line_id],{"plan_qty":qty})
                        else:
                            vals={
                                "forecast_id": sf_id,
                                "customer_id": contact_id,
                                "product_id": prod_id,
                                "uom_id": prod.uom_id.id,
                                "plan_qty": qty,
                            }
                            get_model("sale.forecast.line").create(vals)
                        n+=1
            miss_custs=list(set(miss_custs))
            miss_prods=list(set(miss_prods))
            return {
                "alert": "%d sales forecast quantities imported, %s customers not found: %s, %s products not found: %s"%(n,len(miss_custs),miss_custs,len(miss_prods),miss_prods),
            }
        elif obj.import_type=="aic":
            url="https://advedi.aic.co.th/AiEdi/po/TxtFile/POTALAYN.zip"
            r=requests.get(url)

    def import_uom(self,name,context={}):
        res=get_model("uom").search([["name","=",name]])
        if res:
            uom_id=res[0]
        else:
            vals={
                "name": name,
            }
            uom_id=get_model("uom").create(vals)
        return uom_id

    def import_product(self,code,name,uom_id,context={}):
        vals={
            "code": code,
            "name": name,
            "uom_id": uom_id,
            "type": "stock",
        }
        res=get_model("product").search([["code","=",code]])
        if res:
            prod_id=res[0]
            get_model("product").write([prod_id],vals)
        else:
            prod_id=get_model("product").create(vals)
        return prod_id

Import.register()
