from netforce.model import Model, fields, get_model
from netforce import access


class ProductBrand(Model):
    _inherit = "product.brand"
    _fields = {
        "sync_records": fields.One2Many("sync.record","related_id","Sync Records"),
        "sync_id": fields.Char("Sync ID",function="get_sync_id",function_search="search_sync_id"),
    }

    def get_sync_id(self,ids,context={}):
        vals={}
        for obj in self.browse(ids):
            sync_id=None
            for sync in obj.sync_records:
                sync_id=sync.sync_id
                break
            vals[obj.id]=sync_id
        return vals

    def search_sync_id(self, clause, context={}):
        sync_id = str(clause[2])
        records = get_model("sync.record").search_browse([["related_id","ilike","product.brand,"],["sync_id","=",sync_id]])
        brand_ids = [r.related_id.id  for r in records if r.related_id]
        cond = [["id","in",brand_ids]]
        return cond

ProductBrand.register()
