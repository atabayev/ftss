from django.urls import path
from registration import views

app_name = 'registration'

urlpatterns = [
    # path('<int:cl_id>/save', views.save , name='save'),
    path('reg/', views.registration_new_user, name='new'),
    path('<int:cl_id>/delete', views.delete, name='delete'),
    path('authentication/', views.authentication, name='authentication'),
    path('isordered/', views.is_ordered, name='is_ordered'),
    path('set_fcm_token/', views.save_fcm_token, name='save_fcm_token'),
    path('get_iao/', views.get_info_about_order, name='get_info_about_order'),
    path('make_ao/', views.make_an_order, name='make_an_order'),
    path('cancel_ao/', views.cancel_an_order, name='cancel_an_order'),
    path('dyftfo/', views.do_you_find_translator_for_order, name='do_you_find_translator_for_order'),
    path('dytmo/', views.do_you_translate_my_order, name='do_you_translate_my_order'),
    path('finish_o/', views.finish_order, name='finish_order'),
    path('pay_phys/', views.need_pay_by_physical, name='need_pay_by_physical'),
]
