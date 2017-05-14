import requests
from requests.auth import HTTPBasicAuth
#import BeautifulSoup
import re
import json


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


    def callAPI(self, path, args=None):
        req = self.session.post(self.url + path, data={"csrf_token": self.csrf_token})
        return json.loads(req.content)
