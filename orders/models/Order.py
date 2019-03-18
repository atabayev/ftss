from django.db import models
from ..utils.Utils import validate_file_extension, content_file_name
from translator.models import Translator


class Order(models.Model):
    o_id = models.CharField(max_length=15, unique=True)
    lang = models.CharField(max_length=50)
    pages = models.CharField(max_length=10)
    date_start = models.CharField(max_length=20)
    date_end = models.CharField(max_length=20)
    price = models.CharField(max_length=15)
    direction = models.CharField(max_length=20)
    urgency = models.CharField(max_length=10, default="2")
    customer_id = models.CharField(max_length=15)
    status = models.CharField(max_length=3, default='1')
    file_path = models.CharField(max_length=100, default='unknown')
    file_count = models.CharField(max_length=3, default='0')
    arch_path = models.CharField(max_length=100, default='')
    translated_arch_path = models.CharField(max_length=100, default='')
    translators = models.ManyToManyField(Translator)
    translate_rating = models.CharField(max_length=10, default='')


class Files(models.Model):
    ord_id = models.CharField(max_length=15)
    ord_file = models.FileField(upload_to=content_file_name, validators=[validate_file_extension])

    @property
    def path_to_files(self):
        return content_file_name

