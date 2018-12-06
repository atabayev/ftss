from django.urls import path
from manager import views

app_name = 'manager'

urlpatterns = [
    path('atto/', views.add_translator_to_order, name='add_translator_to_order'),
    path('new/', views.new_manager, name='new_manager'),
    path('authentication/', views.authentication, name='authentication'),
    path('orders/', views.orders, name='orders'),
    path('getallorders/', views.get_all_orders, name='getallorders'),
    path('get_ready_translators/', views.get_ready_translators, name='get_ready_translators'),
    path('gofn/', views.get_orders_file_name, name='get_orders_file_name'),
    path('gof/', views.get_orders_file, name='get_orders_file'),
    path('finish_o/', views.finish_order, name='finish_order'),
]
