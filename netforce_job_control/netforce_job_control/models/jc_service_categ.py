from netforce.model import Model, fields, get_model

class ServiceCateg(Model):
    _name="jc.service.categ"
    _string="Service Category"
    _name_field="full_name"
    _fields={
        "name": fields.Char("Name",required=True),
        "full_name": fields.Char("Category Name",function="get_full_name",search=True,store=True,size=256),
        "parent_id": fields.Many2One("jc.service.categ","Parent Category"),
        "description": fields.Text("Description"),
        "active": fields.Boolean("Active"),
        "comments": fields.One2Many("message","related_id","Comments"),
        "job_sequence_id": fields.Many2One("sequence","Job Sequence"),
        "manager_group_id": fields.Many2One("user.group","Manager User Group"),
    }
    _order="full_name"
    _constraints=["_check_cycle"]
    _defaults={
        "active": True,
    }

    def create(self,vals,**kw):
        new_id=super().create(vals,**kw)
        self.function_store([new_id])
        return new_id

    def write(self,ids,vals,**kw):
        super().write(ids,vals,**kw)
        child_ids=self.search(["id","child_of",ids])
        self.function_store(child_ids)

    def get_full_name(self,ids,context={}):
        vals={}
        for obj in self.browse(ids):
            names=[obj.name]
            p=obj.parent_id
            while p:
                names.append(p.name)
                p=p.parent_id
            full_name=" / ".join(reversed(names))
            vals[obj.id]=full_name
        return vals

ServiceCateg.register()
