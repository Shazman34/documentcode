from netforce.model import Model,get_model

class Trans(Model):
    _inherit="payment.transaction"

    def payment_received(self,ids,context={}):
        print("ALN Trans.payment_received",ids)
        super().payment_received(ids,context=context)
        obj=self.browse(ids[0])
        related=obj.related_id
        if related and related._model=="aln.job":
            job=related
            job.write({"state":"wait_accept","qc_state":"wait_accept","is_paid":True})
            job.trigger("qc_paid")

Trans.register()
