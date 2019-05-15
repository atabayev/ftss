from django.urls import path
from translator import views

app_name = 'translator'

urlpatterns = [
    path('new/', views.new, name='new'),
    path('authentication/', views.authentication, name='authentication'),
    path('get_orders/', views.get_orders, name='get_orders'),
    path('get_my_orders/', views.get_my_orders, name='get_orders'),
    path('get_archive/', views.get_archive, name='get_archive'),
    path('send_archive/', views.send_archive, name='send_archive'),
    path('take_order/', views.take_an_order, name='take_an_order'),
    path('complete_order/', views.complete_order, name='complete_order'),
    path('set_fcm_token/', views.save_fcm_token, name='save_fcm_token'),
    path('cancel_order/', views.cancel_order, name='cancel_order'),
]
