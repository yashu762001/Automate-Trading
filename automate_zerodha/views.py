from django.http import HttpResponse
from twilio.twiml.messaging_response import MessagingResponse
from django.views.decorators.csrf import csrf_exempt
import requests
import json
from decouple import Config, Csv

config = Config('.env')
key = config.get('SECRET_KEY')
access_token = config.get('ACCESS_TOKEN')


@csrf_exempt
def webhook(request):
    incoming_message = request.POST.get('Body', '').lower()

    response_msg = ''
    if incoming_message.lower() == 'hi' or incoming_message.lower() == 'hello':
        response_msg = 'Hello Yash How may i help you ? \n'

    elif incoming_message.lower() == 'get prices':
        calls = [19300, 19350, 19400, 19450, 19500]
        puts = [19550, 19600, 19650, 19700, 19750]

        price_data_calls = {}
        price_data_puts = {}

        for (call, put) in zip(calls, puts):
            headers = {
                "X-Kite-Version": "3",
                "Authorization": f"token {key}:{access_token}"
            }
            resp1 = requests.get(
                f'https://api.kite.trade/quote/ltp?i=NFO:NIFTY23907{call}CE', headers=headers)
            tmp = json.loads(resp1.text)
            print(tmp)
            price_data_calls[f'{call} CE'] = tmp['data'][f'NFO:NIFTY23907{call}CE']['last_price']

            resp1 = requests.get(
                f'https://api.kite.trade/quote/ltp?i=NFO:NIFTY23907{put}PE', headers=headers)
            tmp = json.loads(resp1.text)
            price_data_puts[f'{put} PE'] = tmp['data'][f'NFO:NIFTY23907{put}PE']['last_price']

        str1 = ""
        for call in price_data_calls.keys():
            str1 = str1 + f"{call} : {price_data_calls[call]}" + "\n"

        for put in price_data_puts.keys():
            str1 = str1 + f"{put} : {price_data_puts[put]}" + "\n"

        response_msg = str1

    elif 'buy' in incoming_message.lower():
        arr = incoming_message.split(" ")
        asset = f'NIFTY23907{arr[1].upper()}'
        header = {
            "X-Kite-Version": "3",
            "Authorization": f"token {key}:{access_token}"
        }

        data = {
            "tradingsymbol": asset,
            "exchange": "NFO",
            "transaction_type": "BUY",
            "order_type": "MARKET",
            "quantity": 100,
            "product": "MIS",
            "validity": "DAY"
        }

        resp = requests.post(
            f'https://api.kite.trade/orders/regular', headers=header, data=data)
        if resp.status_code == 200:
            response_msg = resp.text
            t = json.loads(resp.text)
            header = {
                "X-Kite-Version": "3",
                "Authorization": f"token {key}:{access_token}"
            }
            resp1 = requests.get(
                f"https://api.kite.trade/orders", headers=header)

            t = json.loads(resp1.text)
            n = t['data']
            avg = t['data'][n-1]['average_price']

            header = {
                "X-Kite-Version": "3",
                "Authorization": f"token {key}:{access_token}"
            }

            data = {
                "tradingsymbol": asset,
                "exchange": "NFO",
                "transaction_type": "SELL",
                "order_type": "LIMIT",
                "price": avg-4.5,
                "quantity": 100,
                "product": "MIS",
                "validity": "DAY"
            }

            resp2 = requests.post(
                f'https://api.kite.trade/orders/regular', headers=header, data=data)

            header = {
                "X-Kite-Version": "3",
                "Authorization": f"token {key}:{access_token}"
            }

            data = {
                "tradingsymbol": asset,
                "exchange": "NFO",
                "transaction_type": "SELL",
                "order_type": "LIMIT",
                "price": avg+3.5,
                "quantity": 100,
                "product": "MIS",
                "validity": "DAY"
            }

            resp3 = requests.post(
                f'https://api.kite.trade/orders/regular', headers=header, data=data)

            response_msg += '\n'
            response_msg = response_msg + \
                f'STOP LOSS PRICE = {avg-4.5}' + '\n' + \
                f'TARGET PRICE = {avg+3.5}' + '\n'

        else:
            response_msg = resp.text

    twiml_response = MessagingResponse()
    twiml_response.message(response_msg)

    return HttpResponse(str(twiml_response), content_type='application/xml')
