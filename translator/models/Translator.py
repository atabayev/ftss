from django.db import models
# from orders.models import Order


class Translator(models.Model):
    t_id = models.CharField(max_length=15)
    name = models.CharField(max_length=50)
    surname = models.CharField(max_length=100)
    email = models.CharField(max_length=100)
    phone = models.CharField(max_length=15)
    reg_date = models.CharField(max_length=20)
    busy = models.CharField(max_length=5, default='0')
    direction = models.CharField(max_length=50, default='')
    # orders = models.ManyToManyField(Order)


class TranslatorAuth(models.Model):
    t_id = models.CharField(max_length=15, unique=True)
    username = models.CharField(max_length=20, unique=True)
    password = models.CharField(max_length=100)
    token = models.CharField(max_length=100, default="")
    fcm_token = models.CharField(max_length=100, default="")


    @property
    def full_title(self):
        return '{0.t_id} {0.name} {0.surname}'.format(self)

    def __str__(self):
        return '{0.t_id} {0.name} {0.surname} {0.phone}'.format(self)
