from django.http import JsonResponse
from django.shortcuts import render

from registration.models import Client, ClientAuth
from .models import Files
from .models import Order
from .utils.Utils import *


# index
def index(request):
    all_orders = Order.objects.all()
    return render(request, 'orders/index.html', locals())


# new
def new(request):
    if "language" not in request.POST or "comment" not in request.POST or "cid" not in request.POST \
            or "urgency" not in request.POST or "token" not in request.POST:
        return JsonResponse({"response": "error_f", "id": ""})
    try:
        client = Client.objects.get(c_id=request.POST['cid'])
    except Client.DoesNotExist:
        return JsonResponse({"response": "denied", "id": "none"})
    try:
        client_auth = ClientAuth.objects.get(c_id=request.POST["cid"])
    except ClientAuth.DoesNotExist:
        return JsonResponse({"response": "denied", "id": "none"})
    if client_auth.token != request.POST["token"]:
        return JsonResponse({"response": "denied", "id": "none"})
    order = Order()
    oid = generate_id()
    order.o_id = oid
    order.lang_to = request.POST['language']
    order.comment = request.POST['comment']
    order.urgency = request.POST['urgency']
    order.customer_id = client.c_id
    order.date_start = datetime.date.today().strftime("%d.%m.%Y")
    order.time_start = datetime.datetime.now().time().strftime("%H:%M:%S")
    order.file_path = 'orders_files/' + order.o_id + '/'
    order.status = "1"
    files = request.FILES.getlist('files', [])
    cnt = 0
    for f in files:
        new_file = Files()
        new_file.ord_id = order.o_id
        new_file.ord_file = f
        new_file.save()
        cnt += 1
    order.file_count = str(cnt)
    arch_name = create_archive_file(oid + "_", "archives")
    if arch_name == 'error':
        return JsonResponse({"response": "error_a", "id": oid})
    order.arch_path = arch_name
    order.save()
    client.order_status = "1"
    client.save()
    return JsonResponse({"response": "ord_added", "id": oid})


# ordering
def ordering(request):
    return JsonResponse({"response": "end"})


# update
def update(request, ord_id):
    if 'cid' in request.POST and 'name' in request.POST and 'surname' in request.POST and 'email' in request.POST and 'phone' in request.POST and 'name' in request.POST:
        try:
            order = Order.objects.get(pk=ord_id)
        except Client.DoesNotExist as Exc:
            return JsonResponse({"response": "unknown_ord"})
        order.o_id = request.POST['oid']
        order.lang = request.POST['language']
        order.pages = request.POST['pages']
        order.date_start = request.POST['datestart']
        order.date_end = request.POST['dateend']
        order.price = request.POST['price']
        order.direction = request.POST['direction']
        order.urgency = request.POST['urgency']
        order.customer_id = request.POST['customer_id']
        order.f = request.POST['urgency']
        order.reg_date = request.POST['urgency']
        order.save()
        return JsonResponse('registration:index')


def delete(request):
    try:
        order = Order.objects.get(o_id=request.POST["oid"])
    except Order.DoesNotExist:
        return JsonResponse({"response": "unknown_ord"})
    order.delete()
    return JsonResponse({"response": "ok"})
