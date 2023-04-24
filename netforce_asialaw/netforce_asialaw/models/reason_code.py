from netforce.model import Model,get_model,fields

class ReasonCode(Model):
    _inherit="reason.code"
    _fields={
        "type": fields.Selection([["fault", "Fault Code"], ["service_multi_visit", "Service Multi-Visit"], ["service_late_response", "Service Late Response"], ["lost_sale_opport", "Lost Sales Opportunity"], ["cancel_sale_opport","Canceled Sales Opportunity"], ["sale_return","Sales Return"], ["lead_refer","Referred Lead"], ["qc_decline","Quick Consult Decline"]], "Reason Type", search=True, required=True),
    }

ReasonCode.register()
