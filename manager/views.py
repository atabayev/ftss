import datetime
import hashlib
import mimetypes
import os
from wsgiref.util import FileWrapper

from django.core import serializers
from django.http import HttpResponse, JsonResponse, StreamingHttpResponse

from orders.models import Order, TranslateResult
from orders.utils.Utils import create_archive_file
from registration.models.Client import Client, ClientAuth
from registration.utils.Utils import converter_ru_to_lt
from translator.models.Translator import Translator, TranslatorAuth
from translator.utils.Utils import generate_token, send_arch_to_email
from .models.Manager import Manager, ManagerAuth
from .utils.Utils import send_push_notification


# Create your views here.

def add_translator_to_order(request):
    if 'tid' not in request.POST or 'oid' not in request.POST or "token" not in request.POST \
            or "date_end" not in request.POST or "price" not in request.POST or "direction" not in request.POST:
        return JsonResponse({"response": "field_error"})
    try:
        ManagerAuth.objects.get(token=request.POST["token"])
    except ManagerAuth.DoesNotExist:
        return JsonResponse({"response": "denied", "translators": ""})
    try:
        order = Order.objects.get(o_id=request.POST['oid'])
    except Order.DoesNotExist:
        return JsonResponse({"response": "error_no_order", "translators": ""})
    translators = request.POST["tid"].split(',')
    unknown_translator = []
    right_translators = []
    for tr in translators:
        try:
            order.translators.add(Translator.objects.get(t_id=tr.replace(" ", "")))
            right_translators.append(tr)
        except Translator.DoesNotExist:
            unknown_translator.append(tr.replace(" ", ""))
    if len(translators) == len(unknown_translator):
        return JsonResponse({"response": "error_unknown_translators", "translators": unknown_translator})
    try:
        client = Client.objects.get(c_id=order.customer_id)
    except Client.DoesNotExist:
        return JsonResponse({"response": "error_unknown_client", "translators": ""})
    order.date_end = request.POST["date_end"]
    order.price = request.POST["price"]
    order.direction = request.POST["direction"]
    order.status = "2"
    order.save()
    client.order_status = "2"
    client.save()
    customers_fcm = [ClientAuth.objects.get(c_id=order.customer_id).fcm_token]
    send_push_notification("Заказ обработан", "Ваш заказ " + order.o_id + " обработан", customers_fcm)
    return JsonResponse({"response": "ok", "translators": unknown_translator})


def orders(request):
    if request.method.upper() == 'GET' and 'token' in request.GET:
        if request.GET['token'] != 'token123':
            return JsonResponse({"response": "token_error"})
        qs = Order.objects.all()
        qs_json = serializers.serialize('json', qs)
        return HttpResponse(qs_json, content_type='application/json')
    else:
        return JsonResponse({"response": "request_error"})


def get_all_orders(request):
    if "token" not in request.GET or "mid" not in request.GET:
        return JsonResponse({"response:" "error_f"})
    try:
        manager = ManagerAuth.objects.get(m_id=request.GET["mid"])
    except ManagerAuth.DoesNotExist:
        return JsonResponse({"response": "denied"})
    if manager.token != request.GET["token"]:
        return JsonResponse({"response": "error_t"})
    all_orders = Order.objects.all()
    orders_dict = {}
    orders_records = []
    orders_dict["response"] = "ok"
    for order in all_orders:
        translators = order.translators.all()
        translators_text = ""
        for translator in translators:
            translators_text += translator.surname + " " + translator.name + "; "
        record = {"o_id": order.o_id,
                  "lang": order.lang,
                  "pages": order.pages,
                  "date_start": order.date_start,
                  "date_end": order.date_end,
                  "price": order.price,
                  "direction": order.direction,
                  "urgency": order.urgency,
                  "customer_id": order.customer_id,
                  "translator_id": translators_text,
                  "status": order.status,
                  "file_count": order.file_count}
        orders_records.append(record)
    orders_dict["orders"] = orders_records
    return JsonResponse(orders_dict)


def new_manager(request):
    if request.method.upper() != "POST":
        return JsonResponse({"response": "m_error", "id": ""})
    if "password" not in request.POST or "name" not in request.POST or "surname" not in request.POST \
            or "email" not in request.POST or "phone" not in request.POST or "pswd" not in request.POST \
            or "username" not in request.POST or "username" not in request.POST:
        return JsonResponse({"response": "f_error", "id": ""})
    if request.POST["pswd"] != 'for_add':
        return JsonResponse({"response": "p_error", "id": ""})
    manager = Manager()
    manager.name = request.POST["name"]
    manager.surname = request.POST["surname"]
    manager.email = request.POST["email"]
    manager.phone = request.POST["phone"]
    manager.reg_date = datetime.date.today().strftime("%d.%m.%Y")
    tmp_id = '{0}{1}{2}'.format(manager.surname[0], manager.name[0], manager.phone)
    mid = manager.m_id = converter_ru_to_lt(tmp_id)
    manager.save()
    hash_psw = hashlib.md5(request.POST['password'].encode('utf-8')).hexdigest()
    managerAuth = ManagerAuth()
    managerAuth.m_id = mid
    managerAuth.username = request.POST["username"].lower()
    managerAuth.password = hash_psw
    managerAuth.save()
    return JsonResponse({"response": "OK", "id": mid})


def authentication(request):
    if "username" not in request.POST or "password" not in request.POST:
        return JsonResponse({"response": "f_error", "id": "", "token": ""})
    try:
        manager = ManagerAuth.objects.get(username=request.POST["username"].lower())
    except ManagerAuth.DoesNotExist:
        return JsonResponse({"response": "denied", "id": "", "token": ""})
    hash_psw = hashlib.md5(request.POST['password'].encode('utf-8')).hexdigest()
    if hash_psw != manager.password:
        return JsonResponse({"response": "denied", "id": "", "token": ""})
    token = manager.token = generate_token()
    mid = manager.m_id
    manager.save()
    return JsonResponse({"response": "ok", "id": mid, "token": token})


def get_ready_translators(request):
    if "mid" not in request.POST or "token" not in request.POST or "direction" not in request.POST:
        return JsonResponse({"response": "error_f"})
    try:
        manager = ManagerAuth.objects.get(m_id=request.POST["mid"])
    except ManagerAuth.DoesNotExist:
        return JsonResponse({"response": "denied"})
    if manager.token != request.POST['token']:
        return JsonResponse({"response": "denied"})
    try:
        translators = Translator.objects.filter(busy="0")
    except Translator.DoesNotExist:
        return JsonResponse({"response": "not_free"})
    request_direction = request.POST["direction"].replace(" ", "").split(",")
    order_dict = dict()
    order_dict["response"] = "ok"
    translators_list = []
    for translator in translators:
        translator_direction = translator.direction.replace(" ", "").split(",")
        if len(list(set(request_direction) & set(translator_direction))) > 0:
            record = dict()
            record["tid"] = translator.t_id
            record["surname"] = translator.surname
            record["name"] = translator.name
            record["email"] = translator.email
            record["phone"] = translator.phone
            record["direction"] = translator.direction
            translators_list.append(record.copy())
            record.clear()
    order_dict["translators"] = translators_list
    return JsonResponse(order_dict)


def get_orders_file_name(request):
    if "mid" not in request.GET or "token" not in request.GET or "oid" not in request.GET:
        return JsonResponse({"response": "error_f"})
    try:
        manager = ManagerAuth.objects.get(m_id=request.GET.get("mid"))
    except ManagerAuth.DoesNotExist:
        return JsonResponse({"response": "denied"})
    if manager.token != request.GET['token']:
        return JsonResponse({"response": "denied"})
    try:
        order = Order.objects.get(o_id=request.GET.get("oid"))
    except Order.DoesNotExist:
        return JsonResponse({"response": "no_order"})
    return JsonResponse({"response": "ok", "file_name": order.arch_path})


def get_orders_file(request):
    if "mid" not in request.GET or "token" not in request.GET or "oid" not in request.GET:
        return JsonResponse({"response": "error_f"})
    try:
        manager = ManagerAuth.objects.get(m_id=request.GET.get("mid"))
        # return JsonResponse({"response": "denied"})
    except ManagerAuth.DoesNotExist:
        return JsonResponse({"response": "denied"})
    if manager.token != request.GET['token']:
        return JsonResponse({"response": "denied"})
    try:
        order = Order.objects.get(o_id=request.GET.get("oid"))
    except Order.DoesNotExist:
        return JsonResponse({"response": "no_order"})
    the_file = order.arch_path
    file_name = os.path.basename(the_file)
    chunk_size = 8192
    response = StreamingHttpResponse(FileWrapper(open(the_file, 'rb'), chunk_size),
                                     content_type=mimetypes.guess_type(the_file)[0])
    response['Content-Length'] = os.path.getsize(the_file)
    response['Content-Disposition'] = "attachment; filename=%s" % file_name
    return response


def finish_order(request):
    if "mid" not in request.POST or "token" not in request.POST or "oid" not in request.POST or \
            "file" not in request.FILES:
        return JsonResponse({"response": "error_f"})
    try:
        if ManagerAuth.objects.get(m_id=request.POST.get("mid")).token != request.POST["token"]:
            return JsonResponse({"response": "denied"})
        order = Order.objects.get(o_id=request.POST.get("oid"))
        client = Client.objects.get(c_id=order.customer_id)
    except ManagerAuth.DoesNotExist:
        return JsonResponse({"response": "denied"})
    except Order.DoesNotExist:
        return JsonResponse({"response": "no_order"})
    except Client.DoesNotExist:
        return JsonResponse({"response": "no_client"})
    if int(order.status) >= 6:
        return JsonResponse({"response": "order_finished"})
<<<<<<< HEAD
    files = request.FILES.getlist('files', [])
    cnt = 0
    for f in files:
        new_file = TranslateResult()
        new_file.o_id = order.o_id
        new_file.ord_file = f
        new_file.save()
        cnt += 1
    arch_name = create_archive_file(order.o_id, "result")
    if arch_name == 'error':
        return JsonResponse({"response": "error_a", "id": order.o_id})
    order.translated_arch_path = arch_name
=======
    new_file = TranslateResult()
    new_file.o_id = order.o_id
    new_file.ord_file = request.FILES.get('file')
    the_file = new_file.ord_file
    new_file.save()
    order.translated_arch_path = the_file
>>>>>>> b73f5cffaf63986c7b3587bb7eb78359f049b28a
    msg_text = """
        Здравстуйте!
        Ваш заказ №: {0} готов.
        Перевод находится во вложении.    
    """.format(order.o_id)
    if send_arch_to_email(client.email, "Ваш заказ № " + order.o_id + " готов", msg_text, the_file.url):
        order.status = "6"
        translators = order.translators.all()
        order.save()
        fcm_token = [ClientAuth.objects.get(c_id=client.c_id).fcm_token]
        send_push_notification("Заказ завершен", "Результат перевода отправлен Вам на почту", fcm_token)
        fcm_token.clear()
        for translator in translators:
            try:
                fcm_token.append(TranslatorAuth.objects.get(t_id=translator.t_id).fcm_token)
            except TranslatorAuth.DoesNotExist:
                continue
        send_push_notification("Заказ завершен", "Заказ проверен и отправлен заказчику", fcm_token)
        return JsonResponse({"response": "ok", "id": order.o_id})
    else:
        return JsonResponse({"response": "error_se", "id": order.o_id})


def get_all_translator(request):
    if "mid" not in request.GET or "token" not in request.GET:
        return JsonResponse({"response": "error_f"})
    try:
        manager = ManagerAuth.objects.get(m_id=request.GET["mid"])
    except ManagerAuth.DoesNotExist:
        return JsonResponse({"response": "denied"})
    if manager.token != request.GET['token']:
        return JsonResponse({"response": "denied"})
    try:
        translators = Translator.objects.all()
    except Translator.DoesNotExist:
        return JsonResponse({"response": "havent"})
    translator_dict = dict()
    translator_dict["response"] = "ok"
    translator_dict["count"] = translators.count()
    translators_list = []
    for translator in translators:
        record = dict()
        record["tid"] = translator.t_id
        record["surname"] = translator.surname
        record["name"] = translator.name
        record["email"] = translator.email
        record["phone"] = translator.phone
        record["direction"] = translator.direction
        record["reg_date"] = translator.reg_date
        record["busy"] = translator.busy
        translators_list.append(record.copy())
        record.clear()
    translator_dict["translators"] = translators_list
    return JsonResponse(translator_dict)


def get_all_customers(request):
    if "mid" not in request.GET or "token" not in request.GET:
        return JsonResponse({"response": "error_f"})
    try:
        manager = ManagerAuth.objects.get(m_id=request.GET["mid"])
    except ManagerAuth.DoesNotExist:
        return JsonResponse({"response": "denied"})
    if manager.token != request.GET['token']:
        return JsonResponse({"response": "denied"})
    try:
        customers = Client.objects.all()
    except Client.DoesNotExist:
        return JsonResponse({"response": "havent"})
    customer_dict = dict()
    customer_dict["response"] = "ok"
    customer_dict["count"] = customers.count()
    customer_list = []
    for customer in customers:
        record = dict()
        record["tid"] = customer.c_id
        record["surname"] = customer.surname
        record["name"] = customer.name
        record["email"] = customer.email
        record["phone"] = customer.phone
        record["reg_date"] = customer.reg_date
        record["refused_orders"] = customer.refused_orders
        record["completed_orders"] = customer.completed_orders
        record["rating"] = customer.rating
        customer_list.append(record.copy())
        record.clear()
    customer_dict["customers"] = customer_list
    return JsonResponse(customer_dict)
