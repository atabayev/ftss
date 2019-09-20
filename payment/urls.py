from django.urls import path
from manager import views

app_name = 'payment'

urlpatterns = [
    path('get_pk/', views.get_pk, name='get_pk'),
]
