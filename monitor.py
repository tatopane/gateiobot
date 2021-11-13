import os
from datetime import datetime, timedelta
import json
from pushbullet import Pushbullet
from decouple import config
import gate_api
from gate_api.exceptions import ApiException, GateApiException

test = False

with open('settings.json', 'r') as f:
    settings = json.load(f)

pb = Pushbullet(config('PUSHBULLET_API_KEY'))
if not pb:
	raise("Couldn't initialize Pushbullet")
	exit()

conf = gate_api.Configuration(
    key=config('GATEIO_API_KEY'),
    secret=config('GATEIO_API_SECRET')
)

api_client = gate_api.ApiClient(conf)
# Create an instance of the API class
api_instance = gate_api.SpotApi(api_client)
base_currency = 'USDT' # str | Settle currency


for cur in settings.keys():
	if settings[cur]['bounds']:
		last_alert = settings[cur]["last_alert"] if "last_alert" in settings[cur] else None
		try:
			currency_pair = cur + "_" + base_currency
			api_response = api_instance.list_tickers(currency_pair=currency_pair) # returns list of Ticker objects with data
			#print(api_response)
			price = float(api_response[0].last)
		except GateApiException as ex:
		    print("Gate api exception, label: %s, message: %s\n" % (ex.label, ex.message))
		    continue
		except ApiException as e:
		    print("Exception when calling GateioApi: %s\n" % e)
		    continue

		if test or (settings[cur]['bounds'][0] and price <= settings[cur]['bounds'][0]):
			print(cur, price, ' lower than ', settings[cur]['bounds'][0])
			if test or (last_alert and datetime.now()-timedelta(hours=24) <= last_alert):
				print(cur,'should notify', last_alert)
				settings[cur]['last_alert'] = str(datetime.now())
				push = pb.push_note("Crypto Alert: Time to buy", "{} trading at {} (below {})".format(cur,price,settings[cur]['bounds'][0]))

		elif settings[cur]['bounds'][1] and price >= settings[cur]['bounds'][1]:
			print(cur, price, ' higher than ', settings[cur]['bounds'][1])
			if test or (last_alert and datetime.now()-timedelta(hours=24) <= last_alert):
				print(cur,'should notify', last_alert)
				settings[cur]['last_alert'] = str(datetime.now())
				push = pb.push_note("Crypto Alert: Time to sell", "{} trading at {} (above {})".format(cur,price,settings[cur]['bounds'][0]))

		else:
			print(cur, price, str(datetime.now()))

#write it back to the file
with open('settings.json', 'w') as f: ##https://stackoverflow.com/questions/19078170/python-how-would-you-save-a-simple-settings-config-file
   json.dump(settings, f)







