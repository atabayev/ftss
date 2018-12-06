from django.contrib import admin
from orders.models import Order
from .models import Client
from translator.models import Translator


admin.site.register(Client)
admin.site.register(Translator)
