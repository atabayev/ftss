from django.shortcuts import render
from django.http import JsonResponse
from .models import Translator, TranslatorAuth
from orders.models import Order
from .utils.Utils import *
from manager.models.Manager import ManagerAuth
from manager.utils.Utils import send_push_notification
from registration.models.Client import Client, ClientAuth
from registration.utils.Utils import converter_ru_to_lt
import datetime
import hashlib


def index(request):
    all_translators = Translator.objects.all()
    return render(request, 'translator/index.html', locals())


def new(request):
    if "name" not in request.POST or "surname" not in request.POST or "email" not in request.POST \
            or "phone" not in request.POST or "direction" not in request.POST or "token" not in request.POST \
            or "username" not in request.POST or "password" not in request.POST:
        return JsonResponse({"response": "f_error", "id": ""})
    try:
        ManagerAuth.objects.get(token=request.POST["token"])
    except ManagerAuth.DoesNotExist:
        return JsonResponse({"response": "t_error", "id": ""})
    if Translator.objects.filter(phone=request.POST['phone']).exists():
        return JsonResponse({"response": "ex_error", "id": ""})
    translator = Translator()
    translator.name = request.POST['name']
    translator.surname = request.POST['surname']
    translator.email = request.POST['email']
    translator.phone = request.POST['phone']
    translator.direction = request.POST['direction']
    tmp_id = '{0}{1}{2}'.format(translator.surname[0], translator.name[0], translator.phone)
    translator.t_id = converter_ru_to_lt(tmp_id)
    translator.reg_date = datetime.date.today().strftime("%d.%m.%Y")
    translator.busy = "0"
    translator.save()
    hash_pswd = hashlib.md5(request.POST['password'].encode('utf-8')).hexdigest()
    translator_auth = TranslatorAuth()
    translator_auth.t_id = translator.t_id
    translator_auth.username = request.POST["username"].lower()
    translator_auth.password = hash_pswd
    translator_auth.save()
    return JsonResponse({"response": "OK", "id": translator.t_id})


def authentication(request):
    if 'username' not in request.POST or 'password' not in request.POST:
        return JsonResponse({"response": "f_error", "id": "", "token": ""})
    try:
        translator_auth = TranslatorAuth.objects.get(username=request.POST['username'].lower())
    except TranslatorAuth.DoesNotExist:
        return JsonResponse({"response": "denied", "id": "", "token": ""})
    hash_psw = hashlib.md5(request.POST['password'].encode('utf-8')).hexdigest()
    if hash_psw != translator_auth.password:
        return JsonResponse({"response": "denied", "id": "", "token": ""})
    new_token = generate_token()
    t_id = translator_auth.t_id
    translator_auth.token = new_token
    translator_auth.save()
    return JsonResponse({"response": "access", "id": t_id, "token": new_token})


def de_authentication(request):
    # TODO: удалить токен и указать что не онлайн.
    return JsonResponse({"response": "OK"})


def get_archive(request):
    if 'oid' not in request.GET:
        return JsonResponse({"response": "error_f"})
    # TODO: Добавить проверку на ошибку "field_error" в FTST
    oid = request.POST['oid']
    try:
        order = Order.objects.get(o_id=oid)
    except Order.DoesNotExist:
        return JsonResponse({"response": "order not exist"})
    return take_response_for_archive(order.arch_path)


def send_archive(request):
    if 'tid' not in request.POST or 'token' not in request.POST or 'oid' not in request.POST:
        return JsonResponse({"response": "error_f", "data": ""})
    try:
        translator_auth = TranslatorAuth.objects.get(t_id=request.POST['tid'])
    except TranslatorAuth.DoesNotExist:
        return JsonResponse({"response": "denied", "data": ""})
    if request.POST['token'] != translator_auth.token:
        return JsonResponse({"response": "error_t", "data": ""})
    try:
        translator = Translator.objects.get(t_id=translator_auth.t_id)
    except Translator.DoesNotExist:
        return JsonResponse({"response": "error_itb", "data": ""})
    archive = Order.objects.get(o_id=request.POST['oid']).arch_path
    if send_arch_to_email(translator.email,
                          'Файл заказа id:' + request.POST['oid'],
                          'Добрый день \n Файл по вложении!',
                          archive):
        return JsonResponse({"response": "send_email_ok", "data": translator.email})
    else:
        return JsonResponse({"response": "error_send"})


def get_orders(request):
    if 'tid' not in request.POST or 'token' not in request.POST:
        return JsonResponse({"response": "error_f"})
    try:
        translator_auth = TranslatorAuth.objects.get(t_id=request.POST['tid'])
    except TranslatorAuth.DoesNotExist:
        return JsonResponse({"response": "denied"})
    if request.POST['token'] != translator_auth.token:
        return JsonResponse({"response": "denied"})
    try:
        translator = Translator.objects.get(t_id=request.POST['tid'])
    except Translator.DoesNotExist:
        return JsonResponse({"response": "denied"})
    try:
        orders = translator.order_set.filter(status=3)
        # orders = translator.orders.all().filter(orders__status='2')
    except Translator.DoesNotExist:
        return JsonResponse({"response": "no_orders"})
    if len(orders) == 0:
        return JsonResponse({"response": "no_orders"})
    orders_dict = {}
    orders_records = []
    orders_dict["response"] = "ok"
    for translators_orders in orders:
        order_id = translators_orders.o_id
        order_date_end = translators_orders.date_end
        order_lang = translators_orders.lang
        order_direction = translators_orders.direction
        order_pages = translators_orders.pages
        order_price = translators_orders.price
        record = {"id": order_id, "deadline": order_date_end, "language": order_lang,
                  "direction": order_direction, "pageCount": order_pages, "price": order_price}
        orders_records.append(record)
    orders_dict["orders"] = orders_records
    return JsonResponse(orders_dict)


def get_my_orders(request):
    if 'tid' not in request.POST or 'token' not in request.POST:
        return JsonResponse({"response": "error_f"})
    try:
        translator_auth = TranslatorAuth.objects.get(t_id=request.POST['tid'])
    except TranslatorAuth.DoesNotExist:
        return JsonResponse({"response": "denied"})
    if request.POST['token'] != translator_auth.token:
        return JsonResponse({"response": "denied"})
    try:
        translator = Translator.objects.get(t_id=request.POST['tid'])
    except Translator.DoesNotExist:
        return JsonResponse({"response": "denied"})
    try:
        orders = translator.order_set.filter(status=4).filter(status=5)
    except Translator.DoesNotExist:
        return JsonResponse({"response": "no_orders"})
    if len(orders) == 0:
        return JsonResponse({"response": "no_orders"})
    orders_dict = {}
    orders_records = []
    orders_dict["response"] = "ok"
    for translators_orders in orders:
        order_id = translators_orders.o_id
        order_date_end = translators_orders.date_end
        order_lang = translators_orders.lang
        order_direction = translators_orders.direction
        order_pages = translators_orders.pages
        order_price = translators_orders.price
        order_status = translators_orders.status
        record = {"id": order_id, "deadline": order_date_end, "language": order_lang,
                  "direction": order_direction, "pageCount": order_pages, "price": order_price, "status": order_status}
        orders_records.append(record)
    orders_dict["orders"] = orders_records
    return JsonResponse(orders_dict)


def take_an_order(request):
    if "tid" not in request.POST or "oid" not in request.POST or "token" not in request.POST:
        return JsonResponse({"response": "error_f", "data": ""})
    try:
        if TranslatorAuth.objects.get(t_id=request.POST["tid"]).token != request.POST["token"]:
            return JsonResponse({"response": "error_t", "data": ""})
    except TranslatorAuth.DoesNotExist:
        return JsonResponse({"response": "denied", "data": ""})
    try:
        order = Order.objects.get(o_id=request.POST["oid"])
        client = Client.objects.get(c_id=order.customer_id)
    except Order.DoesNotExist:
        return JsonResponse({"response": "error_one", "data": ""})
    except Client.DoesNotExist:
        return JsonResponse({"response": "error_cne", "data": ""})
    if order.status != "3":
        return JsonResponse({"response": "error_s", "data": ""})
    order.status = "4"
    order.translators.clear()
    order.translators.add(Translator.objects.get(t_id=request.POST["tid"]))
    order.save()
    client_fcm_token = [ClientAuth.objects.get(c_id=client.c_id).fcm_token]
    client.order_status = "4"
    client.save()
    send_push_notification("Результат", "Найден подходящий переводчик", client_fcm_token)
    return JsonResponse({"response": "tao_ok", "data": ""})


def complete_order(request):
    if "tid" not in request.POST or "oid" not in request.POST or "token" not in request.POST:
        return JsonResponse({"response": "error_f", "data": ""})
    try:
        if TranslatorAuth.objects.get(t_id=request.POST["tid"]).token != request.POST["token"]:
            return JsonResponse({"response": "error_t", "data": ""})
    except TranslatorAuth.DoesNotExist:
        return JsonResponse({"response": "denied", "data": ""})
    try:
        order = Order.objects.get(o_id=request.POST["oid"])
    except Order.DoesNotExist:
        return JsonResponse({"response": "error_one", "data": ""})
    order.status = "5"
    order.save()
    return JsonResponse({"response": "finish_ok", "data": ""})


def save_fcm_token(request):
    if "tid" not in request.POST or "token" not in request.POST or "fcm_token" not in request.POST:
        return JsonResponse({"response": "error_f"})
    try:
        translator_auth = TranslatorAuth.objects.get(t_id=request.POST["tid"])
    except Client.DoesNotExist:
        return JsonResponse({"response": "denied"})
    if translator_auth.token != request.POST["token"]:
        return JsonResponse({"response": "denied"})
    translator_auth.fcm_token = request.POST["fcm_token"]
    translator_auth.save()
    return JsonResponse({"response": "ok"})

