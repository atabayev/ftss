from django.urls import path
from payment import views

app_name = 'payment'

urlpatterns = [
    path('paying/', views.paying, name='paying'),
]
