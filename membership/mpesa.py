import requests
import base64
from datetime import datetime
from django.conf import settings


def get_mpesa_token():
    url  = "https://sandbox.safaricom.co.ke/oauth/v1/generate?grant_type=client_credentials"
    if settings.MPESA_ENV == 'production':
        url = "https://api.safaricom.co.ke/oauth/v1/generate?grant_type=client_credentials"

    resp = requests.get(url, auth=(
        settings.MPESA_CONSUMER_KEY,
        settings.MPESA_CONSUMER_SECRET
    ))
    return resp.json().get('access_token')


def generate_password():
    timestamp = datetime.now().strftime('%Y%m%d%H%M%S')
    raw       = f"{settings.MPESA_SHORTCODE}{settings.MPESA_PASSKEY}{timestamp}"
    password  = base64.b64encode(raw.encode()).decode()
    return password, timestamp


def stk_push(phone, amount, account_ref, description):
    token    = get_mpesa_token()
    password, timestamp = generate_password()

    base_url = "https://sandbox.safaricom.co.ke"
    if settings.MPESA_ENV == 'production':
        base_url = "https://api.safaricom.co.ke"

    url     = f"{base_url}/mpesa/stkpush/v1/processrequest"
    headers = {"Authorization": f"Bearer {token}"}
    payload = {
        "BusinessShortCode": settings.MPESA_SHORTCODE,
        "Password":          password,
        "Timestamp":         timestamp,
        "TransactionType":   "CustomerPayBillOnline",
        "Amount":            int(amount),
        "PartyA":            phone,
        "PartyB":            settings.MPESA_SHORTCODE,
        "PhoneNumber":       phone,
        "CallBackURL":       settings.MPESA_CALLBACK_URL,
        "AccountReference":  account_ref,
        "TransactionDesc":   description,
    }
    resp = requests.post(url, json=payload, headers=headers)
    return resp.json()