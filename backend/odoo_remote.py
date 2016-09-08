from __future__ import print_function
import xmlrpclib
import time
import sys
from smartcard.scard import *
import smartcard.util
import pickle



class OdooRemote():

    #url = 'https://odoo.fablab-karlsruhe.de'
    url = 'http://127.0.0.1:8069'
    db = 'FabLabKA'
    username = 'admin'
    password = 'admin'
    #username = secret_password.username
    #password = secret_password.password
    machine_name = 'LaserSaur'
    user_level = None
    unlock_time = 5 #how long is the machine unlocked?
    dummy_mode = False
    last_user = ''

    _common = None
    _uid = None
    _models = None
    _mode = None
    _id_cards = None
    _users = None
    _last_acces = 0

    #def main(self):
    #    self.init()
    #    while(True):
    #        self.get_access()
    #        if self._mode == 'error':
    #            return False
    #        #if self.mode == 'backup':
    #            #TODO: Try to go live again
    #        time.sleep(1)

    def init(self):
        if self.dummy_mode:
            self.last_user = 'Max Mustermann'
            return
        try:
            self._common = xmlrpclib.ServerProxy('{}/xmlrpc/2/common'.format(self.url))
            self._uid = self._common.authenticate(self.db, self.username, self.password, {})
            self._models = xmlrpclib.ServerProxy('{}/xmlrpc/2/object'.format(self.url))
            #TODO: Save ID-Cards, Users and Machines locally (in case of odoo/internet failure)
            self._machine = self._models.execute_kw(self.db, self._uid, self.password,
                                    'lab.machine', 'search_read',
                                    [[['name', '=', self.machine_name]]],
                                    {})
            print(self._machine)
            self._id_cards = self._models.execute_kw(self.db, self._uid, self.password,
                                    'lab.id_cards', 'search_read',
                                    [],
                                    {'fields':['card_id', 'status', 'assigned_client']})
            print(self._id_cards)
            self._users = self._models.execute_kw(self.db, self._uid, self.password,
                                    'res.partner', 'search_read',
                                    [],
                                    {'fields':['id']})
            print(self._users)
            #print(self.users)
            #print(self.id_cards)
            #print(self.machine)
            pickle.dump(self._machine, open("db_machine.backup", "wb"))
            pickle.dump(self._id_cards, open("db_id_cards.backup", "wb"))
            pickle.dump(self._users, open("db_users.backup", "wb"))

            print("BACKUP_DB_SAVED")
            self._mode = 'odoo'


        except IOError:
            print("COULD_NOT_OPEN_CONNECTION")
            try:
                print("BACKUP_DB_LOADED")
                self._machine = pickle.load(open("db_machine.backup", "rb"))
                self._id_cards = pickle.load(open("db_id_cards.backup", "rb"))
                self._users = pickle.load(open("db_users.backup", "rb"))
                self._mode='backup'
            except ValueError:
                print("COULD_NOT_LOAD_BACKUP_DB")
                self._mode='error'

        if len(self._machine) != 1:
            print("NO_OR_MULTIPLE_MACHINES_FOUND")
            return False

    def check_access(self, card_number):
        if self.dummy_mode:
            return "Max Mustermann"
        print("card: " + card_number + " ", end="")
        if card_number == None:
            return False

        if self._mode == 'odoo':
            try:
                self._machine = self._models.execute_kw(self.db, self._uid, self.password,
                                        'lab.machine', 'search_read',
                                        [[['name', '=', self.machine_name]]],
                                        {})
                card = self._models.execute_kw(self.db, self._uid, self.password,
                                        'lab.id_cards', 'search_read',
                                        [[['card_id', '=', card_number]]],
                                        {})
            except IOError:
                print("CONNECTIN_FAILED")
                self._mode = 'backup'
        if self._mode == 'backup':
            card = filter(lambda x: x['card_id'] == card_number, self._id_cards)
        if len(card) != 1:
            print("CARD_NOT_FOUND")
            return False
        #print(card[0])
        if card[0]['status'] != 'active':
            print("CARD_NOT_ACTIVE")
            return False
        if card[0]['assigned_client'] == 0:
            print("CARD_NOT_ASSIGNED")
            return False
        if self._mode == 'odoo':
            try:
                client = self._models.execute_kw(self.db, self._uid, self.password,
                                        'res.partner', 'read',
                                        [[card[0]['assigned_client'][0]]],
                                        {'fields': ['name']})
            except IOError:
                print("CONNECTIN_FAILED")
                self._mode = 'backup'
        if self._mode == 'backup':
            client = filter(lambda user: user['id'] == card[0]['assigned_client'][0], self._users)

        if(len(client) != 1):
            print("FUCKED_UP_EVERYTHING")
            self._mode = 'error'
            return False
        client = client[0]
        #TODO: Check if user is member(Mitglied)
        #if client[0]['is_member'] == False:
        #   print("CLIENT_NOT_MEMBER")
        #   return False
        if client['id'] in self._machine[0]['owner_ids']:
            print("CLIENT_IS_OWNER")
            self.user_level = 'owner'
            self.last_user = client['name']
            return client['name'] #Owners get full acces no matter the circumstances
        elif self._machine[0]['status'] == 'r':
            if client['id'] in self._machine[0]['user_ids'] and self._machine[0]['rules'] == 'r':
                print("CLIENT_IS_USER")
                self.user_level = 'user'
                self.last_user = client['name']
                return client['name']
            elif self._machine[0]['rules'] == 'f':
                print("FREE_ACCESS")
                self.user_level = 'free'
                self.last_user = client['name']
                return client['name']
        print("NO_ACCESS")
        return False

    def get_access(self):
        if self.get_access_rfid():
            self._last_acces = time.time()
            print("ACCESS_UNLOCKED")
            return True
        else:
            if (time.time() - self._last_acces) < self.unlock_time:
                print("STILL_UNLOCKED")
                return True
        return False


    def get_access_rfid(self):
        hresult, hcontext = SCardEstablishContext(SCARD_SCOPE_USER)
        if hresult == SCARD_S_SUCCESS:
            hresult, readers = SCardListReaders(hcontext, [])
            if len(readers) > 0:
                reader = readers[0]
                hresult, hcard, dwActiveProtocol = SCardConnect(
                hcontext,
                reader,
                SCARD_SHARE_SHARED,
                SCARD_PROTOCOL_T0 | SCARD_PROTOCOL_T1)
                if hresult == 0:
                    hresult, response = SCardTransmit(hcard,dwActiveProtocol,[0xFF,0xCA,0x00,0x00,0x00])
                    current_card = smartcard.util.toHexString(response)
                    print(current_card)
                    return self.check_access(current_card)
                else:
                    print("NO_CARD")
            else:
                print("NO_READER")
        else:
            print("FAILED")



