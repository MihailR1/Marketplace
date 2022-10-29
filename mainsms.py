
#	При перечислении номеров или иных идентификаторов через запятую, избегайте использования пробелов.
#
#	Что бы указать не все необязательные параметры, необходимо указать имя параметра, при вызове функции, например:
#	sms.create('10000', 'текст сообщения', name='имя рассылки', test=1)	
#	
#	результат любой функции - словарь, элементы словарей описаны на домашней странице сервиса


import requests		# Для работы с http запросами (в нашем случае POST)
import json			# Для работы с ответом сервера (в формате JSON)
import hashlib		# Для шифрования


class SMS:

	headers = {'Content-type' : 'application/x-www-form-urlencoded'}
	
	def __init__(self,p,a):
		self.project=p	# Имя проекта
		self.api_key=a	# API-ключ
		self.url='http://mainsms.ru/api/'		

	# выполнение запроса
	def doRequest (self, rqData, url):

		# формируем словарь
		rqData['project']=self.project	# 1. Добавляем в словарь POST проект
		l=[]
		sign=''
		
		for i in rqData:			# 2. словарь POST переводим в список
			l.append(str(rqData[i]))
		l.sort()					# 3. сортируем в алфавитном порядке
		
		for element in l:			# 4. получаем левую часть sign
			sign=sign+str(element)+';'
		
		sign=sign+str(self.api_key)	# 5. получаем целый нешифрованный sign
		
		sign = hashlib.sha1(sign.encode("utf-8")).hexdigest()	# 6. шифруем sha1
		sign = hashlib.md5(sign.encode("utf-8")).hexdigest()	# 7. шифруем md5

		rqData['sign']=sign		# 8. добавляем sign в POST
		
		r = requests.get(self.url+url, headers=self.headers, params=rqData)
		#print r.url		# Когда что-то идёт не по плану, можно посмотреть GET запрос (через браузер)
		#r = requests.post(self.url+url, headers=self.headers, data=rqData)	#POST работал только с одиночными SMS
		
		print(r.text)
		
		ansver = json.loads(r.text)
		return ansver				

#									#
#			ОДИНОЧНЫЕ СМС			#
#									#
	def sendSMS(self, recipients, message, sender='', run_at='', test=0):		# шлём SMS
		rqData = {
			"recipients": recipients,
			"message" 	: message,
			"test" 		: test
		} 
		if sender != '':
			rqData['sender']=sender		
			
		# если указана дата-время (формат  "дд.мм.гггг чч:мм")
		# часовой пояс настраивается в личном кабинете
		if run_at != '':
			rqData['run_at']=run_at
		return self.doRequest(rqData, 'message/send')

	def getBalance(self):		# узнаём баланс
		rqData = {}
		return self.doRequest(rqData, 'message/balance')
			
	def messagePrice(self, recipients, message):		# узнаём цену сообщений
		rqData = {
			"recipients": recipients,
			"message" 	: message,
			"sender" 	: self.sender
		} 
		return self.doRequest(rqData, 'message/price')
	
	def info(self, phones ):	# узнаём информацию о номерах
		rqData = {"phones" : phones} 
		return self.doRequest(rqData, 'message/info')				
	
	def statusSMS(self, messages_id):	# узнаём статус SMS
		rqData = {"messages_id" : messages_id} 
		return self.doRequest(rqData, 'message/status')
		
#									#
#			РАССЫЛКИ				#
#									#
	def create(self, include, message, exclude=0, sender='', run_at='', slowtime='', slowsize='', name='', test=0):	# Создание смс рассылки
		rqData = {
			"include"	: include,
			"message"	: message
		}
		if sender != '':
			rqData['sender']=sender

		if slowtime != '':
			rqData['slowtime']=slowtime

		if slowsize != '':
			rqData['slowsize']=slowsize

		if name != '':
			rqData['name']=name

		if run_at != '':
			rqData['run_at']=run_at

		if exclude != 0:
			rqData['exclude']=exclude

		if test != 0:
			rqData['test']=test

		return self.doRequest(rqData, 'sending/create')

	def groups(self, type):	# Запрос групп
		rqData = {"type" : type} 
		return self.doRequest(rqData, 'sending/groups')

	def status(self, id):	# Запрос статуса рассылки
		rqData = {"id" : id} 
		return self.doRequest(rqData, 'sending/status')
	
