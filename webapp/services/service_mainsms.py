import requests
import json
import hashlib

from loguru import logger


class SMS:
    headers = {'Content-type': 'application/x-www-form-urlencoded'}

    def __init__(self, p, a):
        self.project = p
        self.api_key = a
        self.url = 'http://mainsms.ru/api/'

    def doRequest(self, rqData, url):
        rqData['project'] = self.project
        l = []
        sign = ''

        for i in rqData:
            l.append(str(rqData[i]))
        l.sort()

        for element in l:
            sign = sign + str(element) + ';'

        sign = sign + str(self.api_key)
        sign = hashlib.sha1(sign.encode("utf-8")).hexdigest()
        sign = hashlib.md5(sign.encode("utf-8")).hexdigest()
        rqData['sign'] = sign
        r = requests.get(self.url + url, headers=self.headers, params=rqData)
        ansver = json.loads(r.text)
        logger.info(r.text)

        return ansver

    def sendSMS(self, recipients, message, sender='', run_at='', test=0):
        rqData = {
            "recipients": recipients,
            "message": message,
            "test": test
        }
        if sender != '':
            rqData['sender'] = sender
        if run_at != '':
            rqData['run_at'] = run_at
        return self.doRequest(rqData, 'message/send')

    def getBalance(self):
        rqData = {}
        return self.doRequest(rqData, 'message/balance')

    def messagePrice(self, recipients, message):
        rqData = {
            "recipients": recipients,
            "message": message,
            "sender": self.sender
        }
        return self.doRequest(rqData, 'message/price')

    def info(self, phones):
        rqData = {"phones": phones}
        return self.doRequest(rqData, 'message/info')

    def statusSMS(self, messages_id):
        rqData = {"messages_id": messages_id}
        return self.doRequest(rqData, 'message/status')

    def create(self, include, message, exclude=0, sender='', run_at='', slowtime='', slowsize='', name='', test=0):
        rqData = {
            "include": include,
            "message": message
        }
        if sender != '':
            rqData['sender'] = sender
        if slowtime != '':
            rqData['slowtime'] = slowtime
        if slowsize != '':
            rqData['slowsize'] = slowsize
        if name != '':
            rqData['name'] = name
        if run_at != '':
            rqData['run_at'] = run_at
        if exclude != 0:
            rqData['exclude'] = exclude
        if test != 0:
            rqData['test'] = test

        return self.doRequest(rqData, 'sending/create')

    def groups(self, type):
        rqData = {"type": type}
        return self.doRequest(rqData, 'sending/groups')

    def status(self, id):
        rqData = {"id": id}
        return self.doRequest(rqData, 'sending/status')
