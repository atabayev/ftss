import requests
from django.shortcuts import render
from requests.auth import HTTPBasicAuth
from django.http import JsonResponse
from registration.models import ClientAuth

# Create your views here.

pkey = "pk_aac81032584d2d7c9ebc09c85591b"
pswd = "28e2a76f04e607634b64e45431d4b0d0"


def paying(request):
    if "amount" not in request.POST or "currency" not in request.POST or "ipAddress" not in request.POST \
            or "name" not in request.POST or "cardCryptogramPacket" not in request.POST or "accountId" not in request.POST\
            or "invoiceId" not in request.POST or "email" not in request.POST:
        return JsonResponse({"response": "field_error"})
    try:
        if ClientAuth.objects.get(c_id=request.POST.get("accountId")).token != request.POST["token"]:
            return JsonResponse({"response": "denied"})
    except ClientAuth.DoesNotExist:
        return JsonResponse({"response": "denied"})
    data = {
        "Amount": request.POST.get("amount"),
        "Currency": request.POST.get("currency"),
        "IpAddress": request.POST.get("ipAddress"),
        "Name": request.POST.get("name"),
        "CardCryptogramPacket": request.POST.get("cardCryptogramPacket"),
        "AccoundIt": request.POST.get("accountId"),
        "invoiceId": request.POST.get("invoiceId"),
        "email": request.POST.get("email")
    }
    # отправка запроса на сервер CloudPayments
    r = requests.post("https://api.cloudpayments.ru/payments/cards/charge", data, auth=HTTPBasicAuth(pkey, pswd))
    if r.status_code != 200:
        return JsonResponse({"response": "send_error", "message": "charge_error"})
    cloud_payments_resp = r.json()
    # если успешно прошёл платёж
    if cloud_payments_resp["Success"] is True:
        return JsonResponse({"response": "completed"})
    # если транзакция отклонена или требует 3DS
    if cloud_payments_resp["Success"] is False and cloud_payments_resp["Message"] is None:
        # если транзакция отклонена
        if "ReasonCode" in cloud_payments_resp["Model"]:
            return JsonResponse({"response": "declined", "reasonCode": cloud_payments_resp["Model"]["ReasonCode"]})
        # если требует 3DS
        else:
            return JsonResponse({"response": "3ds", "md": cloud_payments_resp["Model"]["TransactionId"],
                                 "paReq": cloud_payments_resp["Model"]["PaReq"],
                                 "acsUrl": cloud_payments_resp["Model"]["AcsUrl"]})
        # если некоректно сформирован запрос
    if cloud_payments_resp["Success"] is False and cloud_payments_resp["Message"] is not None:
        return JsonResponse({"response": "pay_error", "message": cloud_payments_resp["Message"]})
    return JsonResponse({"response": "unknown_error"})


def term_url(request):
    md = request.POST.get("MD")
    pa_res = request.POST.get("PaRes")
    url = "https://api.cloudpayments.ru/payments/cards/post3ds"
    data = {
        "TransactionId": md,
        "PaRes": pa_res
    }
    r = requests.post(url, data, auth=HTTPBasicAuth(pkey, pswd))
    if r.status_code != 200:
        return render(request, "payment/pay_result.html", {"status_code": r.status_code, "isSuccess": ""})
    cloud_payments_resp = r.json()
    # если успешно прошёл платёж
    if cloud_payments_resp["Success"] is True:
        return render(request, "payment/pay_result.html", {"status_code": r.status_code, "isSuccess": "ПРОШЛА УСПЕШНО"})
    # ели транзакция отклонена
    if cloud_payments_resp["Success"] is False \
            and cloud_payments_resp["Message"] is None \
            and "ReasonCode" in cloud_payments_resp["Model"]:
        return render(request, "payment/pay_result.html", {"status_code": r.status_code, "isSuccess": "ОТКЛОНЕНА"})
    # если некоректно сформирован запрос
    if cloud_payments_resp["Success"] is False and cloud_payments_resp["Message"] is not None:
        return render(request, "payment/pay_result.html", {"status_code": r.status_code, "isSuccess": "НЕКОРЕКТНА"})
    return JsonResponse({"response": "unknown_error"})
