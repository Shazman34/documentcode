from netforce.model import Model,fields,get_model
from netforce import utils
import xlrd
from decimal import *

def read_cell_str(sheet,i,j):
    s=sheet.cell(i,j).value
    if isinstance(s,str):
        return s
    return str(int(s))

def read_cell_dec(sheet,i,j):
    s=sheet.cell(i,j).value
    if not s:
        return None
    if not isinstance(s,str):
        s=str(int(s))
    return Decimal(s)

def read_cell_date(book,sheet,i,j):
    val=sheet.cell(i,j).value
    if not val:
        return None
    d=xlrd.xldate.xldate_as_datetime(41889, book.datemode)
    return d.strftime("%Y-%m-%d")

class BatchImport(Model):
    _name="batch.import"
    _fields={
        "file": fields.File("XLS File",required=True),
    }

    def do_import(self,ids,context={}):
        print("BatchImport.do_import",ids)
        obj=self.browse(ids[0])
        path=utils.get_file_path(obj.file)
        book=xlrd.open_workbook(path)
        self.import_products(book)
        self.import_customers(book)
        self.import_suppliers(book)
        self.import_accounts(book)
        self.import_cust_invoices(book)
        self.import_supp_invoices(book)
        self.import_payments(book)
        return {
            "flash": "Import successfull",
        }

    def import_products(self,book):
        sheet=book.sheet_by_name("Products")
        uom_name="Unit"
        res=get_model("uom").search([["name","=",uom_name]])
        if not res:
            raise Exception("UoM not found: %s"%uom_name)
        uom_id=res[0]
        for i in range(1, sheet.nrows):
            code=read_cell_str(sheet,i,0)
            name=sheet.cell(i,1).value
            vals={
                "code": code,
                "name": name,
                "type": "stock",
                "uom_id": uom_id,
            }
            res=get_model("product").search([["code","=",code]])
            if not res:
                get_model("product").create(vals)

    def import_customers(self,book):
        sheet=book.sheet_by_name("Customers")
        for i in range(1, sheet.nrows):
            code=read_cell_str(sheet,i,0)
            name=sheet.cell(i,1).value
            vals={
                "code": code,
                "name": name,
                "type": "org",
                "customer": True,
            }
            res=get_model("contact").search([["code","=",code]])
            if not res:
                get_model("contact").create(vals)

    def import_suppliers(self,book):
        sheet=book.sheet_by_name("Suppliers")
        for i in range(1, sheet.nrows):
            code=read_cell_str(sheet,i,0)
            name=sheet.cell(i,1).value
            vals={
                "code": code,
                "name": name,
                "type": "org",
                "supplier": True,
            }
            res=get_model("contact").search([["code","=",code]])
            if not res:
                get_model("contact").create(vals)

    def import_accounts(self,book):
        sheet=book.sheet_by_name("Accounts")
        for i in range(1, sheet.nrows):
            code=read_cell_str(sheet,i,0)
            name=sheet.cell(i,1).value
            vals={
                "type": "cash",
                "code": code,
                "name": name,
            }
            res=get_model("account.account").search([["code","=",code]])
            if not res:
                get_model("account.account").create(vals)

    def import_cust_invoices(self,book):
        all_inv=[]
        sheet=book.sheet_by_name("Customer Invoices")
        prev_inv_num=None
        for i in range(1, sheet.nrows):
            cust_code=read_cell_str(sheet,i,0)
            inv_num=read_cell_str(sheet,i,1)
            inv_date=read_cell_date(book,sheet,i,2)
            inv_due_date=read_cell_date(book,sheet,i,3)
            prod_code=read_cell_str(sheet,i,4)
            desc=read_cell_str(sheet,i,5)
            unit_price=read_cell_dec(sheet,i,6)
            qty=read_cell_dec(sheet,i,7)
            acc_code=read_cell_str(sheet,i,8)
            tax_rate=read_cell_str(sheet,i,9)
            track1=read_cell_str(sheet,i,10)
            track2=read_cell_str(sheet,i,11)
            amount=read_cell_dec(sheet,i,12)
            currency=read_cell_str(sheet,i,13)
            currency_rate=read_cell_dec(sheet,i,14)
            if prev_inv_num is None or inv_num!=prev_inv_num:
                if cust_code:
                    res=get_model("contact").search([["code","=",cust_code]])
                    if not res:
                        raise Exception("Customer not found: %s"%code)
                    cust_id=res[0]
                else:
                    cust_id=None
                if currency:
                    res=get_model("currency").search([["code","=",currency]])
                    if not res:
                        raise Exception("Currency not found: %s"%currency)
                    currency_id=res[0]
                else:
                    currency_id=None
                if currency_id:
                    res=get_model("account.account").search([["type","=","receivable"],["currency_id","=",currency_id]])
                    if not res:
                        raise Exception("Receivable account not found for currency %s"%currency)
                    acc_id=res[0]
                else:
                    acc_id=None
                inv_vals={
                    "contact_id": cust_id,
                    "number": inv_num,
                    "date": inv_date,
                    "due_date": inv_due_date,
                    "currency_id": currency_id,
                    "currency_rate": currency_rate,
                    "type": "out",
                    "inv_type": "invoice",
                    "account_id": acc_id,
                    "lines": [],
                }
                all_inv.append(inv_vals)
                prev_inv_num=inv_num
            if prod_code:
                res=get_model("product").search([["code","=",prod_code]])
                if not res:
                    raise Exception("Product not found: %s"%prod_code)
                prod_id=res[0]
            else:
                prod_id=None
            if acc_code:
                res=get_model("account.account").search([["code","=",acc_code]])
                if not res:
                    raise Exception("Account not found: %s"%acc_code)
                acc_id=res[0]
            else:
                acc_id=None
            if tax_rate:
                res=get_model("account.tax.rate").search([["code","=",tax_rate]])
                if not res:
                    raise Exception("Tax rate not found: %s"%tax_rate)
                tax_rate_id=res[0]
            else:
                tax_rate_id=None
            if track1:
                res=get_model("account.track.categ").search([["code","=",track1]])
                if not res:
                    raise Exception("Tracking category not found: %s"%track1)
                track1_id=res[0]
            else:
                track1_id=None
            if track2:
                res=get_model("account.track.categ").search([["code","=",track2]])
                if not res:
                    raise Exception("Tracking category not found: %s"%track2)
                track2_id=res[0]
            else:
                track2_id=None
            line_vals={
                "product_id": prod_id,
                "description": desc or "/",
                "unit_price": unit_price,
                "qty": qty,
                "account_id": acc_id,
                "tax_id": tax_rate_id,
                "track_id": track1_id,
                "track2_id": track2_id,
                "amount": amount,
            }
            inv_vals["lines"].append(("create",line_vals))
        for inv_vals in all_inv:
            res=get_model("account.invoice").search([["number","=",inv_vals["number"]],["type","=","out"]])
            if res:
                continue
            try:
                inv_id=get_model("account.invoice").create(inv_vals)
                get_model("account.invoice").post([inv_id])
            except Exception as e:
                raise Exception("Failed to import invoice %s: %s"%(inv_vals.get("number"),e))

    def import_supp_invoices(self,book):
        all_inv=[]
        sheet=book.sheet_by_name("Supplier Invoices")
        prev_inv_num=None
        for i in range(1, sheet.nrows):
            contact_code=read_cell_str(sheet,i,0)
            inv_num=read_cell_str(sheet,i,1)
            inv_date=read_cell_date(book,sheet,i,2)
            inv_due_date=read_cell_date(book,sheet,i,3)
            prod_code=read_cell_str(sheet,i,4)
            desc=read_cell_str(sheet,i,5)
            unit_price=read_cell_dec(sheet,i,6)
            qty=read_cell_dec(sheet,i,7)
            acc_code=read_cell_str(sheet,i,8)
            tax_rate=read_cell_str(sheet,i,9)
            track1=read_cell_str(sheet,i,10)
            track2=read_cell_str(sheet,i,11)
            amount=read_cell_dec(sheet,i,12)
            currency=read_cell_str(sheet,i,13)
            currency_rate=read_cell_dec(sheet,i,14)
            if prev_inv_num is None or inv_num!=prev_inv_num:
                if contact_code:
                    res=get_model("contact").search([["code","=",contact_code]])
                    if not res:
                        raise Exception("Customer not found: %s"%code)
                    contact_id=res[0]
                else:
                    contact_id=None
                if currency:
                    res=get_model("currency").search([["code","=",currency]])
                    if not res:
                        raise Exception("Currency not found: %s"%currency)
                    currency_id=res[0]
                else:
                    currency_id=None
                if currency_id:
                    res=get_model("account.account").search([["type","=","payable"],["currency_id","=",currency_id]])
                    if not res:
                        raise Exception("Payable account not found for currency %s"%currency)
                    acc_id=res[0]
                else:
                    acc_id=None
                inv_vals={
                    "contact_id": contact_id,
                    "number": inv_num,
                    "date": inv_date,
                    "due_date": inv_due_date,
                    "currency_id": currency_id,
                    "currency_rate": currency_rate,
                    "type": "in",
                    "inv_type": "invoice",
                    "account_id": acc_id,
                    "lines": [],
                }
                all_inv.append(inv_vals)
                prev_inv_num=inv_num
            if prod_code:
                res=get_model("product").search([["code","=",prod_code]])
                if not res:
                    raise Exception("Product not found: %s"%prod_code)
                prod_id=res[0]
            else:
                prod_id=None
            if acc_code:
                res=get_model("account.account").search([["code","=",acc_code]])
                if not res:
                    raise Exception("Account not found: %s"%acc_code)
                acc_id=res[0]
            else:
                acc_id=None
            if tax_rate:
                res=get_model("account.tax.rate").search([["code","=",tax_rate]])
                if not res:
                    raise Exception("Tax rate not found: %s"%tax_rate)
                tax_rate_id=res[0]
            else:
                tax_rate_id=None
            if track1:
                res=get_model("account.track.categ").search([["code","=",track1]])
                if not res:
                    raise Exception("Tracking category not found: %s"%track1)
                track1_id=res[0]
            else:
                track1_id=None
            if track2:
                res=get_model("account.track.categ").search([["code","=",track2]])
                if not res:
                    raise Exception("Tracking category not found: %s"%track2)
                track2_id=res[0]
            else:
                track2_id=None
            line_vals={
                "product_id": prod_id,
                "description": desc or "/",
                "unit_price": unit_price,
                "qty": qty,
                "account_id": acc_id,
                "tax_id": tax_rate_id,
                "track_id": track1_id,
                "track2_id": track2_id,
                "amount": amount,
            }
            inv_vals["lines"].append(("create",line_vals))
        for inv_vals in all_inv:
            res=get_model("account.invoice").search([["number","=",inv_vals["number"]],["type","=","in"]])
            if res:
                continue
            try:
                inv_id=get_model("account.invoice").create(inv_vals)
                get_model("account.invoice").post([inv_id])
            except Exception as e:
                raise Exception("Failed to import invoice %s: %s"%(inv_vals.get("number"),e))

    def import_payments(self,book):
        sheet_names = book.sheet_names()
        for sheet_name in sheet_names:
            if not sheet_name.startswith("Payments -"):
                continue
            acc_name=sheet_name.replace("Payments -","").strip()
            res=get_model("account.account").search([["name","=",acc_name]])
            if not res:
                raise Exception("Account not found: %s"%acc_name)
            acc_id=res[0]
            sheet=book.sheet_by_name(sheet_name)
            for i in range(1, sheet.nrows):
                date=read_cell_date(book,sheet,i,0)
                if not date:
                    continue
                try:
                    desc=read_cell_str(sheet,i,1)
                    contact_code=read_cell_str(sheet,i,2)
                    inv_num=read_cell_str(sheet,i,3)
                    inv_amt=read_cell_str(sheet,i,4)
                    adj_amt=read_cell_str(sheet,i,5)
                    pl_acc_code=read_cell_str(sheet,i,6)
                    in_amt=read_cell_str(sheet,i,7)
                    out_amt=read_cell_str(sheet,i,8)
                    bal_amt=read_cell_str(sheet,i,9)
                    if contact_code:
                        res=get_model("contact").search([["code","=",contact_code]])
                        if not res:
                            raise Exception("Contact not found: %s"%contact_code)
                        contact_id=res[0]
                    else:
                        contact_id=None
                    if pl_acc_code:
                        res=get_model("account.account").search([["code","=",pl_acc_code]])
                        if not res:
                            raise Exception("Account not found: %s"%pl_acc_code)
                        pl_acc_id=res[0]
                    else:
                        pl_acc_id=None
                    pmt_vals={
                        "account_id": acc_id,
                        "date": date,
                        "contact_id": contact_id,
                        "lines": [],
                    }
                    if in_amt:
                        pmt_vals["type"]="in"
                        if inv_num:
                            pmt_vals["pay_type"]="invoice"
                            res=get_model("account.invoice").search([["number","=",inv_num],["contact_id","=",contact_id]])
                            if not res:
                                raise Exception("Invoice not found %s (%s)"%(inv_num,contact_code))
                            inv_id=res[0]
                            line_vals={
                                "type": "invoice",
                                "invoice_id": inv_id,
                                "amount": in_amt,
                                "amount_invoice": inv_amt or in_amt,
                            }
                        else:
                            pmt_vals["pay_type"]="direct"
                            line_vals={
                                "type": "direct",
                                "account_id": pl_acc_id,
                                "amount": in_amt,
                            }
                    elif out_amt:
                        pmt_vals["type"]="out"
                        if inv_num:
                            pmt_vals["pay_type"]="invoice"
                            res=get_model("account.invoice").search([["number","=",inv_num],["contact_id","=",contact_id]])
                            if not res:
                                raise Exception("Invoice not found %s (%s)"%(inv_num,contact_code))
                            inv_id=res[0]
                            line_vals={
                                "type": "invoice",
                                "invoice_id": inv_id,
                                "amount": out_amt,
                                "amount_invoice": inv_amt or out_amt,
                            }
                        else:
                            pmt_vals["pay_type"]="direct"
                            line_vals={
                                "type": "direct",
                                "account_id": pl_acc_id,
                                "amount": out_amt,
                            }
                    else:
                        raise Exception("Missing received or spent amount")
                    pmt_vals["lines"].append(("create",line_vals))
                    # XXX: pmt key
                    pmt_id=get_model("account.payment").create(pmt_vals,context={"type":pmt_vals["type"]})
                    get_model("account.payment").post([pmt_id])
                except Exception as e:
                    raise Exception("Failed to import payment %s-%s: %s"%(acc_name,date,e))

BatchImport.register()
