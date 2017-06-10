import odoo_remote
import odooHelper

class Odoo:
    remote = None

    def __init__(self, username, password, url, db,):
        self.remote = odoo_remote.OdooRemote(username, password, url, db, True)

    def getWebInfo(self):
        out = {
            'services': self.remote.services,
            'materials': self.remote.materials,
        }
        return out

    # def setInfo(self, info):

