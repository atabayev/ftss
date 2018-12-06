from django.urls import path
from orders import views

app_name='orders'

urlpatterns = [
    path('', views.index, name='index'),
    path('new/', views.new , name='new'),
    path('delete/', views.delete, name='delete'),

    ]

