import json
import traceback
import backend.datedecoder
import os
from backend.erp.odoo.odooHelper import *


class Odoo:
    remote = None
    last_user = {'name': 'Max Mustermann', 'id': 0}
    _id_cards = None
    _users = None
    _materials = None #ToDo add default
    _services = None #ToDo add default
    _machine = None
    _helper = None
    _active = False

    def __init__(self, username, password, url, db):
        print("Initializing Odoo remote connection")
        try:
            self._helper = OdooHelper(username, password, url, db)
            self._machine = self._helper.callAPI("/machine_management/getMachine/")
            self._id_cards = self._helper.callAPI("/machine_management/getIdCards/")
            self._users = self._helper.callAPI("/machine_management/getUsers/")
            self._materials = self._helper.callAPI(
                "/machine_management/getProductByTag/" + str(self._machine['machine_tag_1']) + "/")
            self._services = self._helper.callAPI(
                "/machine_management/getProductByTag/" + str(self._machine['machine_tag_2']) + "/")

            with open('machine.json', 'w') as file:
                json.dump(self._machine, file, indent=4, separators=(',', ': '))
            with open('id_cards.json', 'w') as file:
                json.dump(self._id_cards, file, indent=4, separators=(',', ': '))
            with open('users.json', 'w') as file:
                json.dump(self._users, file, indent=4, separators=(',', ': '))
            with open('materials.json', 'w') as file:
                json.dump(self._materials, file, indent=4, separators=(',', ': '))
            with open('services.json', 'w') as file:
                json.dump(self._services, file, indent=4, separators=(',', ': '))

            print("Odoo Database loaded and saved locally")
            self._active = True

        except:
            print("Couldn't open Database, trying to load backup...")
            traceback.print_exc()
            try:
                with open('machine.json') as file:
                    self._machine = json.load(file)
                with open('id_cards.json') as file:
                    self._id_cards = json.load(file)
                with open('users.json') as file:
                    self._users = json.load(file)
                with open('materials.json') as file:
                    self.materials = json.load(file)
                with open('services.json') as file:
                    self.services = json.load(file)
                print("Backup loaded!")
            except IOError:
                print("Couldn't find or load local backup Database.")
                print("Shutting down LaserSaurApp, try starting without Odoo support.")
                exit(1)

    def check_access(self, card_number):
        if not card_number:
            return "Missing ID Card"
        card_number = card_number.upper()
        card = filter(lambda id_card: id_card['card_id'] == card_number, self._id_cards)
        if len(card) != 1:
            return "Unregistered ID Card!"
        card = card[0]
        if card['status'] != 'a':
            return "Unactivated ID Card"
        if card['assigned_client'] == 0:
            print("Unassigned ID Card")
            return "Unassigned ID Card!"

        client = filter(lambda user: user['id'] == card['assigned_client'], self._users)
        if len(client) != 1:
            return "Client not found!"
        client = client[0]
        if client['id'] in self._machine['owner_ids']:
            self.last_user = {'name': client['name'], 'id': client['id']}
            return "access"  # Owners get full acces no matter the circumstances
        elif self._machine['status'] == 'r':
            if client['id'] in self._machine['user_ids'] and self._machine['rules'] == 'r':
                self.last_user = {'name': client['name'], 'id': client['id']}
                return "access"
        elif self._machine['rules'] == 'f':
            self.last_user = {'name': client['name'], 'id': client['id']}
            return "access"
        return "User not allowed!"

    def get_con_status(self):
        return self._active

    def getWebInfo(self):
        out = {
            'services': self._services,
            'materials': self._materials,
        }
        return out

    def setInfo(self, info):
        if not info['user_id']:
            info['user_id'] = -1 # ToDo better simply return?
        info['client_id'] = info['user_id']
        info['odoo_material_qty'] = 1

        if self._active and info['user_id'] >= 0:
            self._helper.callAPI("/machine_management/registerUsage/", info)

        joblist = []
        if os.path.isfile('jobs.json'):
            with open('jobs.json', 'r') as file:
                joblist = json.load(file)
        joblist.append(info)
        with open('jobs.json', 'w') as file:
            json.dump(joblist, file, default=backend.datedecoder.default,
                      indent=4, separators=(',', ': '))

    def get_user(self, email):
        if not self._active:
            return -1
        out = filter(lambda user: user['email'] == email, self._users)
        if len(out) != 1:
            return -1
        return out[0]

    def get_product(self, id):
        if not self._active:
            return 0
        ret_product = filter(lambda product: product['id'] == int(id), self.materials)
        if len(ret_product) != 1:
            return None
        return ret_product[0]

    def get_service(self, id):
        if not self._active:
            return 0
        ret_service = filter(lambda service: service['id'] == int(id), self.services)
        if len(ret_service) != 1:
            return None
        return ret_service[0]