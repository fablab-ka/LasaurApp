import requests
import re
import backend.json
import backend.datedecoder


class OdooHelper:

    def __init__(self, username, password, url, db):
        self.username = username
        self.password = password
        self.url = url
        self.db = db
        self.connected = False

        #Open Session with Odoo
        self.session = requests.session()
        if db:
            req1 = self.session.get(self.url + "/web?db=" + self.db)
        else:
            req1 = self.session.get(self.url + "/web")
        self.csrf_token = re.findall(r'name="csrf_token" value="(.+?)"', req1.content)
        payload = {
            "login": self.username,
            "password": self.password,
            "csrf_token": self.csrf_token,
        }
        req2 = self.session.post(self.url + "/web/login", data=payload)

        if req2.status_code == 200:
            self.connected = True
            print("Odoo connection established!")
        else:
            print(req2.status_code)

        #TODO find way of checking if /web/login or /web get reached


    def callAPI(self, path, data=None):
        payload = None
        if data:
            try:
                data = backend.json.dumps(data, default=backend.datedecoder.default, indent=4, separators=(',', ': '))
            except:
                print("data is not JSON-compatible: " + str(data))
                data = None
        req = self.session.post(self.url + path, data={"csrf_token": self.csrf_token, "params": data})
        try:
            return backend.json.loads(req.content)
        except ValueError:
            return False