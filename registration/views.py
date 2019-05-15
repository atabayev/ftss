from django.shortcuts import render, get_object_or_404
from django.http import Http404, HttpResponseRedirect
from django.urls import reverse
from django.http import JsonResponse
import datetime
from .models import Client, ClientAuth
from orders.models import Order
from .utils.Utils import converter_ru_to_lt, send_sms_to_client
from translator.utils.Utils import generate_token
from manager.utils.Utils import send_push_notification
from translator.models.Translator import TranslatorAuth


def get_sms_for_registration(request):
    if "phone" not in request.POST:
        return JsonResponse({"response": "error_field"})
    send_sms_to_client(request.POST["phone"])
    return JsonResponse({"response": "OK"})


def get_sms_for_authentication(request):
    if "phone" not in request.GET:
        return JsonResponse({"response": "error_field", "token": ""})
    try:
        client = Client.objects.get(phone=request.GET["phone"])
    except Client.DoesNotExist:
        return JsonResponse({"response": "denied", "token": ""})
    client.token = generate_token()
    client.save()
    send_sms_to_client(client.phone)
    return JsonResponse({"response": "OK", "token": client.token})


# Registration new User
def registration_new_user(request):
    if 'name' in request.POST and 'surname' in request.POST and 'email' in request.POST and 'phone' in request.POST:
        ph = request.POST['phone']
        phone_number = ph[len(ph)-10:]
        # if phone_number[0] == "+":
        #     client.phone = phone_number[1:]git commi
        # else:
        #     client.phone = phone_number
        if Client.objects.filter(phone=phone_number).exists():
            return JsonResponse({"response": "record_ex", "id": ""})
        client = Client()
        client.name = request.POST['name']
        client.surname = request.POST['surname']
        client.email = request.POST['email']
        client.phone = phone_number
        tmp_id = '{0}{1}{2}'.format(client.surname[0], client.name[0], client.phone)
        client.c_id = converter_ru_to_lt(tmp_id)
        client.reg_date = datetime.date.today().strftime("%d.%m.%Y")
        client.save()
        client_auth = ClientAuth()
        client_auth.c_id = client.c_id
        client_auth.phone_number = client.phone
        new_token = generate_token()
        client_auth.token = new_token
        client_auth.save()
        return JsonResponse({"response": "ok", "id": client.c_id, "token": new_token})
    else:
        return JsonResponse({"response": "field_er", "id": ""})


# Authentication
def authentication(request):
    if "phone" not in request.POST:
        return JsonResponse({"response": "error_f", "id": "", "status": ""})
    try:
        client = Client.objects.get(phone=request.POST['phone'])
    except Client.DoesNotExist as Exc:
        return JsonResponse({"response": "denied", "id": "", "status": ""})
    try:
        client_auth = ClientAuth.objects.get(c_id=client.c_id)
    except ClientAuth.DoesNotExist:
        return JsonResponse({"response": "denied", "id": client.c_id, "token": "", "status": ""})
    new_token = generate_token()
    client_auth.token = new_token
    client_auth.save()
    try:
        order = Order.objects.exclude(status="0").exclude(status="7").get(customer_id=client.c_id)
    except:
        return JsonResponse({"response": "access", "id": client.c_id, "token": new_token, "status": "0"})
    return JsonResponse({"response": "access", "id": client.c_id, "token": new_token, "status": order.status})


def delete(request, cl_id):
    client = get_object_or_404(Client, pk=cl_id)
    client.delete()
    return HttpResponseRedirect(reverse('registration:index'))


def is_ordered(request):
    if 'cid' not in request.POST:
        return JsonResponse({"response": "field_er", "status": ""})
    try:
        client = Client.objects.get(c_id=request.POST['cid'])
    except Client.DoesNotExist:
        return JsonResponse({"response": "unknown_cl", "status": ""})
    return JsonResponse({"response": "ok", "status": client.order_status})
    # if client.is_ordered == "0":
    #     return JsonResponse({"response": "not_ordered", "id": ""})
    # if client.is_ordered == "1":
    #     try:
    #         order = Order.objects.get(customer_id=client.c_id)
    #     except Order.DoesNotExist:
    #         client.is_ordered = "0"
    #         client.save()
    #         return JsonResponse({"response": "not_ordered", "id": ""})
    #     return JsonResponse({"response": "ordered", "id": order.o_id})


def save_fcm_token(request):
    if "cid" not in request.POST or "token" not in request.POST or "fcm_token" not in request.POST:
        return JsonResponse({"response": "error_f"})
    try:
        client_auth = ClientAuth.objects.get(c_id=request.POST["cid"])
    except Client.DoesNotExist:
        return JsonResponse({"response": "denied"})
    if client_auth.token != request.POST["token"]:
        return JsonResponse({"response": "denied"})
    client_auth.fcm_token = request.POST["fcm_token"]
    client_auth.save()
    return JsonResponse({"response": "ok"})


def get_info_about_order(request):
    if "cid" not in request.POST or "token" not in request.POST or "oid" not in request.POST:
        return JsonResponse({"response": "error_f", "orderId": "", "language": "", "pagesCount": "", "price": "",
                             "dateEnd": "", "urgency": "", })
    try:
        client_id = Client.objects.get(c_id=request.POST["cid"]).c_id
        if ClientAuth.objects.get(c_id=client_id).token != request.POST["token"]:
            return JsonResponse({"response": "denied", "orderId": "", "language": "", "pagesCount": "", "price": "",
                                 "dateEnd": "", "urgency": ""})
        order = Order.objects.get(o_id=request.POST["oid"])
    except Client.DoesNotExist:
        return JsonResponse({"response": "denied", "orderId": "", "language": "", "pagesCount": "", "price": "",
                             "dateEnd": "", "urgency": ""})
    except ClientAuth.DoesNotExist:
        return JsonResponse({"response": "denied", "orderId": "", "language": "", "pagesCount": "", "price": "",
                             "dateEnd": "", "urgency": ""})
    except Order.DoesNotExist:
        return JsonResponse({"response": "error_o", "orderId": "", "language": "", "pagesCount": "", "price": "",
                             "dateEnd": "", "urgency": ""})
    if order.status == "2":
        return JsonResponse({"response": "ready", "orderId": order.o_id, "language": order.lang_from+'-'+order.lang_to,
                             "pagesCount": order.pages, "price": order.price_to_client, "dateEnd": order.date_end,
                             "urgency": order.urgency})
    else:
        return JsonResponse({"response": "no", "orderId": "", "language": "", "pagesCount": "", "price": "",
                             "dateEnd": "", "urgency": ""})


def make_an_order(request):
    if "cid" not in request.POST or "token" not in request.POST or "oid" not in request.POST:
        return JsonResponse({"response": "error_f"})
    try:
        if ClientAuth.objects.get(c_id=request.POST["cid"]).token == request.POST["token"]:
            order = Order.objects.get(o_id=request.POST["oid"])
        else:
            return JsonResponse({"response": "denied"})
    except ClientAuth.DoesNotExist:
        return JsonResponse({"response": "denied"})
    except Order.DoesNotExist:
        return JsonResponse({"response": "error_no_order"})
    order.status = "3"
    client = Client.objects.get(c_id=request.POST["cid"])
    client.order_status = "3"
    client.save()
    translators = order.translators.all()
    order.save()
    translators_fcm_token = []
    for translator in translators:
        translators_fcm_token.append(TranslatorAuth.objects.get(t_id=translator.t_id).fcm_token)
    send_push_notification("Новый заказ", "Поступил новый заказ: " + order.o_id, translators_fcm_token)
    return JsonResponse({"response": "ok"})


def cancel_an_order(request):
    if "cid" not in request.POST or "token" not in request.POST or "oid" not in request.POST:
        return JsonResponse({"response": "error_f"})
    try:
        if ClientAuth.objects.get(c_id=request.POST["cid"]).token == request.POST["token"]:
            order = Order.objects.get(o_id=request.POST["oid"])
        else:
            return JsonResponse({"response": "denied"})
    except ClientAuth.DoesNotExist:
        return JsonResponse({"response": "denied"})
    except Order.DoesNotExist:
        return JsonResponse({"response": "error_no_order"})
    order.status = "0"
    order.save()
    return JsonResponse({"response": "cancel_ok"})


def do_you_find_translator_for_order(request):
    if "cid" not in request.POST or "token" not in request.POST or "oid" not in request.POST:
        return JsonResponse({"response": "error_f"})
    try:
        if ClientAuth.objects.get(c_id=request.POST["cid"]).token == request.POST["token"]:
            order = Order.objects.get(o_id=request.POST["oid"])
        else:
            return JsonResponse({"response": "denied"})
    except ClientAuth.DoesNotExist:
        return JsonResponse({"response": "denied"})
    except Order.DoesNotExist:
        return JsonResponse({"response": "error_no_order"})
    if order.status == "4":
        return JsonResponse({"response": "yes"})
    else:
        return JsonResponse({"response": "no"})


def do_you_translate_my_order(request):
    if "cid" not in request.POST or "token" not in request.POST or "oid" not in request.POST:
        return JsonResponse({"response": "error_f"})
    try:
        if ClientAuth.objects.get(c_id=request.POST["cid"]).token == request.POST["token"]:
            order = Order.objects.get(o_id=request.POST["oid"])
        else:
            return JsonResponse({"response": "denied"})
    except ClientAuth.DoesNotExist:
        return JsonResponse({"response": "denied"})
    except Order.DoesNotExist:
        return JsonResponse({"response": "error_no_order"})
    if order.status == "6":
        return JsonResponse({"response": "yes"})
    else:
        return JsonResponse({"response": "no"})


def finish_order(request):
    if "cid" not in request.POST or "token" not in request.POST or "oid" not in request.POST \
            or "rating" not in request.POST:
        return JsonResponse({"response": "error_f"})
    try:
        if ClientAuth.objects.get(c_id=request.POST["cid"]).token == request.POST["token"]:
            order = Order.objects.get(o_id=request.POST["oid"])
        else:
            return JsonResponse({"response": "denied"})
    except ClientAuth.DoesNotExist:
        return JsonResponse({"response": "denied"})
    except Order.DoesNotExist:
        return JsonResponse({"response": "error_no_order"})
    order.status = "7"
    order.translate_rating = request.POST['rating']
    order.save()
    return JsonResponse({"response": "ok"})

