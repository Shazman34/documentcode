from netforce.controller import Controller
from netforce.model import get_model
from netforce import database
from netforce import access

class PaymentReceived(Controller):
    _path="/l2g_payment_received"

    def get(self):
        self.write("RECEIVEOK")

    def post(self):
        self.write("RECEIVEOK")

PaymentReceived.register()
