from netforce.model import Model, fields, get_model

class BatchJob(Model):
    _name="jc.batch.job"
    _transient=True

    def create_jobs(self,ids,context={}):
        return get_model("job").batch_create()

BatchJob.register()
