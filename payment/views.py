from django.http import JsonResponse
from registration.models import ClientAuth

# Create your views here.


pk = "pk_aac81032584d2d7c9ebc09c85591b"


def get_pk(request):
    if "cid" not in request.POST or "token" not in request.POST:
        return JsonResponse({"response": "error_f", "key": "none"})
    try:
        client = ClientAuth.objects.get(c_id=request.POST.get("cid"))
    except ClientAuth.DoesNotExist:
        return JsonResponse({"response": "denied", "key": "none"})
    if request.POST.get("token") != client.token:
        return JsonResponse({"response": "denied", "key": "none"})
    return JsonResponse({"response": "pk_ok", "key": pk})


