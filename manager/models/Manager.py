from django.db import models
# from orders.models import Order


class Manager(models.Model):
    m_id = models.CharField(max_length=15, unique=True, null=False)
    name = models.CharField(max_length=50, default='')
    surname = models.CharField(max_length=50, default='')
    email = models.CharField(max_length=100, default='')
    phone = models.CharField(max_length=15, default='')
    reg_date = models.CharField(max_length=20, default='')


class ManagerAuth(models.Model):
    m_id = models.CharField(max_length=15, unique=True)
    username = models.CharField(max_length=20, unique=True)
    password = models.CharField(max_length=100)
    token = models.CharField(max_length=50)
