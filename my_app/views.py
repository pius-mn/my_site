from django.http import HttpResponse
import requests
from requests.auth import HTTPBasicAuth
import json
from django.http import JsonResponse
from .env import MpesaAccessToken, LipanaMpesaPpassword
from .models import MpesaDeposits
from django.views.decorators.csrf import csrf_exempt


def getAccessToken(request):
    consumer_key = 'EmAmcJJDPbUgm5g7xRhawDZkRE1z1Ur'
    consumer_secret = 'QbgkZGRHYdnqQLT'
    api_URL = 'https://sandbox.safaricom.co.ke/oauth/v1/generate?grant_type=client_credentials'

    r = requests.get(api_URL, auth=HTTPBasicAuth(consumer_key, consumer_secret))
    mpesa_access_token = json.loads(r.text)
  
    validated_mpesa_access_token = mpesa_access_token['access_token']

    return HttpResponse(validated_mpesa_access_token)

def lipa_na_mpesa_online(request):
    access_token = MpesaAccessToken.validated_mpesa_access_token
    api_url = "https://sandbox.safaricom.co.ke/mpesa/stkpush/v1/processrequest"
    headers = {"Authorization": "Bearer %s" % access_token}
    request = {
        "BusinessShortCode": LipanaMpesaPpassword.Business_short_code,
        "Password": LipanaMpesaPpassword.decode_password,
        "Timestamp": LipanaMpesaPpassword.lipa_time,
        "TransactionType": "CustomerPayBillOnline",
        "Amount": 1,
        "PartyA": '254759267471',  # replace with your phone number to get stk push
        "PartyB": LipanaMpesaPpassword.Business_short_code,
        "PhoneNumber": '254759267471',  # replace with your phone number to get stk push
        "CallBackURL": "https://piusdeveloper.pythonanywhere.com/api/v1/c2b/confirmation",
        "AccountReference": "pius",
        "TransactionDesc": "Testing stk push"
    }

    response = requests.post(api_url, json=request, headers=headers)
    return HttpResponse('success')
@csrf_exempt
def register_urls(request):
    access_token = MpesaAccessToken.validated_mpesa_access_token
    api_url = "https://sandbox.safaricom.co.ke/mpesa/c2b/v1/registerurl"
    headers = {"Authorization": "Bearer %s" % access_token}
    options = {"ShortCode":LipanaMpesaPpassword.Test_c2b_shortcode,
               "ResponseType": "Completed",
               "ConfirmationURL": "https://piusdeveloper.pythonanywhere.com/api/v1/c2b/confirmation",
               "ValidationURL": "https://piusdeveloper.pythonanywhere.com/api/v1/c2b/validation"}
    response = requests.post(api_url, json=options, headers=headers)
    return HttpResponse(response.text)
@csrf_exempt
def call_back(request):
    pass
@csrf_exempt
def validation(request):
    context = {
        "ResultCode": 0,
        "ResultDesc": "Accepted"
    }
    return JsonResponse(context)
@csrf_exempt
def confirmation(request):
    mpesa_body =request.body.decode('utf-8')
    mpesa_payment = json.loads(mpesa_body)
    payment = MpesaDeposits(
       
        phone_number=mpesa_payment['Body']['stkCallback']['CallbackMetadata']['Item'][4]['Value'],
        reference=mpesa_payment['Body']['stkCallback']['CallbackMetadata']['Item'][1]['Value'],
        transaction_date=mpesa_payment['Body']['stkCallback']['CallbackMetadata']['Item'][3]['Value'],
        amount=mpesa_payment['Body']['stkCallback']['CallbackMetadata']['Item'][0]['Value'],
       
    )
    payment.save()
    context = {
        "ResultCode": 0,
        "ResultDesc": "Accepted"
    }
    return JsonResponse(dict(context))
