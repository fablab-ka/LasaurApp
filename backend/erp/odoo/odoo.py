import odoo_remote
import odooHelper
import json
import backend.datedecoder
import os


class Odoo:
    remote = None

    def __init__(self, username, password, url, db):
        self.remote = odoo_remote.OdooRemote(username, password, url, db, True)

    def get_con_status(self):
        return self.remote._mode == 'odoo'

    def getWebInfo(self):
        out = {
            'services': self.remote.services,
            'materials': self.remote.materials,
        }
        return out

    def setInfo(self, info):
        if not info['user_id']:
            info['user_id'] = 3
        info['client_id'] = info['user_id']
        info['odoo_material_qty'] = 1

        if self.get_con_status():
            self.remote.helper.callAPI("/machine_management/registerUsage/", info)

        list = []
        if os.path.isfile('jobs.json'):
            with open('jobs.json', 'r') as file:
                list = json.load(file)
        list.append(info)
        with open('jobs.json', 'w') as file:
            json.dump(list, file, default=backend.datedecoder.default, indent=4, separators=(',', ': '))

