from netforce.model import Model,fields,get_model

class Order(Model):
    _inherit="production.order"

    def copy_to_inv_tg(self,ids,context={}):
        obj=self.browse(ids[0])
        res=get_model("contact").search([["code","=","TG"]])
        if not res:
            raise Exception("Customer code not found: TG")
        contact_id=res[0]
        inv_vals = {
            "type": "out",
            "inv_type": "invoice",
            "contact_id": contact_id,
            "lines": [],
            "company_id": obj.company_id.id,
            "ref": obj.number,
            "related_id": "production.order,%s"%obj.id,
            "memo": "TG Invoice for RM of %s"%obj.number,
        }
        if not obj.bom_id:
            raise Exception("Missing BoM")
        for comp in obj.components:
            prod = comp.product_id
            line_vals = {
                "product_id": prod.id,
                "description": prod.description or "/",
                "qty": comp.qty_issued,
                "uom_id": comp.uom_id.id,
                "unit_price": 0, # XXX
                "account_id": prod.sale_account_id.id,
                "tax_id": prod.sale_tax_id.id,
            }
            line_vals["amount"]=line_vals["qty"]*line_vals["unit_price"]
            inv_vals["lines"].append(("create",line_vals))
        if not inv_vals["lines"]:
            raise Exception("Nothing to invoice")
        inv_id = get_model("account.invoice").create(inv_vals, {"type": "out", "inv_type": "invoice"})
        inv=get_model("account.invoice").browse(inv_id)
        return {
            "next": {
                "name": "view_invoice",
                "active_id": inv_id,
            },
            "flash": "Invoice %s created from production order" % inv.number,
            "invoice_id": inv_id,
        }

    def copy_to_inv_tg_cust(self,ids,context={}):
        obj=self.browse(ids[0])
        contact_id=obj.customer_id.id
        if not contact_id:
            raise Exception("Customer not found")
        res=get_model("company").search([["code","=","TG"]])
        if not res:
            raise Exception("Company code not found: TG")
        company_id=res[0]
        inv_vals = {
            "type": "out",
            "inv_type": "invoice",
            "contact_id": contact_id,
            "lines": [],
            "company_id": company_id,
            "ref": obj.number,
            "related_id": "production.order,%s"%obj.id,
            "memo": "TG customer invoice for %s"%obj.number,
        }
        prod = obj.product_id
        if not obj.qty_received:
            raise Exception("No finished goods received yet.")
        line_vals = {
            "product_id": prod.id,
            "description": prod.description or "/",
            "qty": obj.qty_received,
            "uom_id": obj.uom_id.id,
            "unit_price": 0, # XXX
            "account_id": prod.sale_account_id.id,
            "tax_id": prod.sale_tax_id.id,
        }
        line_vals["amount"]=line_vals["qty"]*line_vals["unit_price"]
        inv_vals["lines"].append(("create",line_vals))
        inv_id = get_model("account.invoice").create(inv_vals, {"type": "out", "inv_type": "invoice"})
        inv=get_model("account.invoice").browse(inv_id)
        return {
            "next": {
                "name": "view_invoice",
                "active_id": inv_id,
            },
            "flash": "Invoice %s created from production order" % inv.number,
            "invoice_id": inv_id,
        }

    def copy_to_pick_tg_cust(self,ids,context={}):
        obj = self.browse(ids)[0]
        pick_vals = {
            "type": "out",
            "ref": obj.number,
            "related_id": "production.order,%s" % obj.id,
            "lines": [],
        }
        res=get_model("stock.location").search([["type","=","customer"]])
        if not res:
            raise Exception("Customer location not found")
        cust_loc_id=res[0]
        prod=obj.product_id
        line_vals = {
            "product_id": prod.id,
            "qty": obj.qty_received,
            "uom_id": obj.uom_id.id,
            "location_from_id": obj.location_id.id,
            "location_to_id": cust_loc_id,
            "cost_price": prod.cost_price or 0,
            "cost_amount": (prod.cost_price or 0)*obj.qty_received,
        }
        pick_vals["lines"].append(("create", line_vals))
        pick_id = get_model("stock.picking").create(pick_vals, context={"pick_type": "out"})
        pick = get_model("stock.picking").browse(pick_id)
        return {
            "next": {
                "name": "pick_out",
                "mode": "form",
                "active_id": pick_id,
            },
            "flash": "Goods issue %s created from production order %s" % (pick.number, obj.number),
            "pick_id": pick_id,
        }

    def tg_make_po_packing(self, ids, context={}):
        res=get_model("company").search([["code","=","TG"]])
        if not res:
            raise Exception("Company code not found: TG")
        tg_company_id=res[0]
        suppliers = {}
        sale=None
        for obj in self.browse(ids):
            if obj.state=="voided":
                continue
            if not sale:
                sale=obj.sale_id
            for line in obj.components:
                prod = line.product_id
                if not prod:
                    continue
                if not prod.categ_id or prod.categ_id.code!="PACKAGING":
                    continue
                if not prod.suppliers:
                    raise Exception("Missing supplier for product '%s' code '%s'" % (prod.name,prod.code))
                supplier_id = prod.suppliers[0].supplier_id.id
                qtys=suppliers.setdefault(supplier_id,{})
                k=(prod.id,line.uom_id.id)
                if k not in qtys:
                    qtys[k]=0
                purch_qty=line.qty_planned-line.qty_stock
                qtys[k]+=purch_qty
        po_ids = []
        for supplier_id, qtys in suppliers.items():
            purch_vals = {
                "contact_id": supplier_id,
                "ref": sale and sale.number,
                "related_id": sale and "sale.order,%s"%sale.id or None,
                "lines": [],
                "company_id": tg_company_id,
            }
            for (prod_id,purch_uom_id),purch_qty in qtys.items(): # XXX: line order
                prod = get_model("product").browse(prod_id)
                loc_id=prod.locations[0].location_id.id if prod.locations else None
                line_vals = {
                    "product_id": prod_id,
                    "description": prod.description or "/",
                    "qty": purch_qty,
                    "uom_id": purch_uom_id,
                    "unit_price": prod.purchase_price or 0,
                    "tax_id": prod.purchase_tax_id.id,
                    "location_id": loc_id,
                }
                purch_vals["lines"].append(("create", line_vals))
            po_id = get_model("purchase.order").create(purch_vals)
            po_ids.append(po_id)
        return {
            "next": {
                "name": "purchase",
            },
            "flash": "%s purchase orders created"%len(po_ids),
            "purchase_ids": po_ids,
        }

    def tg_make_po_fruit(self, ids, context={}):
        res=get_model("company").search([["code","=","TG"]])
        if not res:
            raise Exception("Company code not found: TG")
        tg_company_id=res[0]
        res=get_model("contact").search([["code","=","KFF"]])
        if not res:
            raise Exception("Contact code not found: KFF")
        kff_contact_id=res[0]
        sale=None
        qtys={}
        for obj in self.browse(ids):
            if obj.state=="voided":
                continue
            if not sale:
                sale=obj.sale_id
            for line in obj.components:
                prod = line.product_id
                if not prod:
                    continue
                if prod.categ_id and prod.categ_id.code=="PACKAGING":
                    continue
                qty_stock=max(0,line.qty_stock)
                #purch_qty=line.qty_planned-qty_stock
                purch_qty=line.qty_planned
                if purch_qty<=0:
                    continue
                k=(prod.id,line.uom_id.id)
                if k not in qtys:
                    qtys[k]=0
                qtys[k]+=purch_qty
        purch_vals = {
            "contact_id": kff_contact_id,
            "ref": sale and sale.number,
            "related_id": sale and "sale.order,%s"%sale.id or None,
            "lines": [],
            "company_id": tg_company_id,
            "delivery_date": sale.due_date, # XXX
        }
        #res=get_model("product").search([["code","=","LABOR"]])
        #if not res:
        #    raise Exception("Product code not found: LABOR")
        #labor_prod_id=res[0]
        #labor_prod=get_model("product").browse(labor_prod_id)
        for obj in self.browse(ids):
            prod=obj.product_id
            line_vals = {
                "product_id": prod.id,
                "description": "Labor for %s [%s]"%(prod.name,prod.code),
                "qty": obj.qty_planned,
                "uom_id": obj.uom_id.id,
                "unit_price": prod.labor_cost or 0,
                "tax_id": prod.purchase_tax_id.id,
            }
            purch_vals["lines"].append(("create", line_vals))
        if qtys:
            for (prod_id,purch_uom_id),purch_qty in qtys.items(): # XXX: line order
                prod = get_model("product").browse(prod_id)
                loc_id=prod.locations[0].location_id.id if prod.locations else None
                line_vals = {
                    "product_id": prod_id,
                    "description": prod.description or "/",
                    "qty": purch_qty,
                    "uom_id": purch_uom_id,
                    "unit_price": prod.purchase_price or 0,
                    "tax_id": prod.purchase_tax_id.id,
                    "location_id": loc_id,
                }
                purch_vals["lines"].append(("create", line_vals))
            po_id = get_model("purchase.order").create(purch_vals)
            purch=get_model("purchase.order").browse(po_id)
            res=purch.copy_to_supplier_sale(context={"confirm_order":True})
            sale_id=res["sale_id"]
            self.write(ids,{"related_id":"sale.order,%s"%sale_id,"sale_id":sale_id}) # XXX: KFF MO linked to KFF SO, not TG SO...
        return {
            "next": {
                "name": "purchase",
            },
            "flash": "1 purchase order created.",
        }

Order.register()
