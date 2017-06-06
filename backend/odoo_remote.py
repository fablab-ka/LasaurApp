from __future__ import print_function
import time
from odooHelper import *

import traceback

class OdooRemote():
    url = None
    db = None
    username = 'admin'
    password = 'admin'
    machine_name = 'LaserSaur' #TODO get machine name from Odoo (new machine field)
    user_level = None
    unlock_time = 5 #how many seconds is the machine unlocked?
    dummy_mode = False
    sell_mode = False
    last_user = {'name':'Max Mustermann', 'id':0}
    use_odoo = False

    _common = None
    _uid = None
    _models = None
    _mode = None
    _id_cards = None
    _users = None
    _last_acces = 0
    products_product = None
    _product_category = None
    _material_tag_id = 0
    _laser_tag_id = 0
    materials = None
    services = None


    #def main(self):
    #    self.init()
    #    while(True):
    #        self.get_access()
    #        if self._mode == 'error':
    #            return False
    #        #if self.mode == 'backup':
    #            #TODO: Try to go live again
    #        time.sleep(1)

    def __init__(self, username, password, url, db, use_odoo):
        self.username = username
        self.password = password
        self.url = url
        self.db = db
        self.use_odoo = use_odoo
        if use_odoo:
            self.init()


    def init(self):
        print("Initializing Odoo remote connection")
        if self.dummy_mode:
            self.last_user = {'name':'Max Mustermann', 'id':'0'}
        try:
            self.helper = OdooHelper(self.username, self.password, self.url, self.db)
            self._machine = self.helper.callAPI("/machine_management/getMachine/1")
            self._id_cards = self.helper.callAPI("/machine_management/getIdCards/")
            self._users = self.helper.callAPI("/machine_management/getUsers/")
            self.materials = self.helper.callAPI("/machine_management/getProductByTag/" + str(self._machine['machine_tag_1']) + "/")
            self.services = self.helper.callAPI("/machine_management/getProductByTag/" + str(self._machine['machine_tag_2']) + "/")

            with open('machine.json', 'w') as file:
                json.dump(self._machine, file, indent=4, separators=(',', ': '))
            with open('id_cards.json', 'w') as file:
                json.dump(self._id_cards, file, indent=4, separators=(',', ': '))
            with open('users.json', 'w') as file:
                json.dump(self._users, file, indent=4, separators=(',', ': '))
            with open('materials.json', 'w') as file:
                json.dump(self.materials, file, indent=4, separators=(',', ': '))
            with open('services.json', 'w') as file:
                json.dump(self.services, file, indent=4, separators=(',', ': '))

            print("Odoo Database loaded and saved locally")
            self._mode = 'odoo'


        except IOError, requests.exceptions.RequestException:

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
                self._mode='backup'
                print("Backup loaded!")
            except IOError:
                print("Couldn't find or load local backup Database.")
                print("Shutting down LaserSaurApp, try starting without Odoo support.")
                exit(1)
                self._mode='error'

        if not self._machine:
            print("Odoo error: No matching machine found")
            return False

    def check_access(self, card_number):
        if self.dummy_mode or not self.use_odoo:
            return "access"
        if card_number == None:
            return "Missing ID Card"
        card_number = card_number.upper()
        card = filter(lambda x: x['card_id'] == card_number, self._id_cards)
        if len(card) != 1:
            print("card " + card_number + " was not found!")
            return "Unregistered ID Card"
        card = card[0]
        if card['status'] != 'a':
            print("Odoo warning: Card is not active!")
            return "Unactivated ID Card"
        if card['assigned_client'] == 0:
            print("Unassigned ID Card")
            return False
        client = filter(lambda user: user['id'] == card['assigned_client'], self._users)

        if(len(client) != 1):
            print("Odoo Error: Fucked up everything, contact Philip Caroli")
            self._mode = 'error'
            return "Error, call Philip C."
        client = client[0]
        if client['id'] in self._machine['owner_ids']:
            #print("CLIENT_IS_OWNER: " + client['name'])
            self.user_level = 'owner'
            self.last_user = {'name':client['name'], 'id':client['id']}
            return "access" #Owners get full acces no matter the circumstances
        elif self._machine['status'] == 'r':
            if client['id'] in self._machine['user_ids'] and self._machine['rules'] == 'r':
                #print("CLIENT_IS_USER: " + client['name'])
                self.user_level = 'user'
                self.last_user = {'name':client['name'], 'id':client['id']}
                return "access"
            elif self._machine['rules'] == 'f':
                #print("free access")
                self.user_level = 'free'
                self.last_user = {'name':client['name'], 'id':client['id']}
                return "access"
        return "User not allowed"

    def get_access(self):
        if self.get_access_rfid():
            self._last_acces = time.time()
            return True
        else:
            if (time.time() - self._last_acces) < self.unlock_time:
                return True
        return False

    def get_product(self, id):
        if not self.use_odoo:
            return 0
        ret_product = filter(lambda product: product['id'] == int(id), self.materials)
        if len(ret_product) != 1:
            return None
        return ret_product[0]

    def get_service(self, id):
        if not self.use_odoo:
            return 0
        ret_service = filter(lambda service: service['id'] == int(id), self.services)
        if len(ret_service) != 1:
            return None
        return ret_service[0]



