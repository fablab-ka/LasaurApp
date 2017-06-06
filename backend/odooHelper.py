import requests
import re
import json
import datedecoder


class OdooHelper:

    def __init__(self, username, password, url, db):
        self.username = username
        self.password = password
        self.url = url
        self.db = db

        #Open Session with Odoo
        self.session = requests.session()
        req1 = self.session.get(self.url + "/web?db=" + self.db)
        self.csrf_token = re.findall(r'name="csrf_token" value="(.+?)"', req1.content)
        payload = {
            "login": self.username,
            "password": self.password,
            "csrf_token": self.csrf_token,
        }
        req2 = self.session.post(self.url + "/web/login", data=payload)

        #TODO find way of checking if /web/login or /web get reached


    def callAPI(self, path, data=None):
        print("API call " + path)
        payload = None
        if data:
            try:
                data = json.dumps(data, default=datedecoder.default, indent=4, separators=(',', ': '))
            except:
                print("data is not JSON-compatible: " + str(data))
                data = None
        req = self.session.post(self.url + path, data={"csrf_token": self.csrf_token, "params": data})
        try:
            return json.loads(req.content)
        except ValueError:
            print("Couldn't decode JSON Element")
            return False