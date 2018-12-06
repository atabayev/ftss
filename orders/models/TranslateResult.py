from django.db import models
from ..utils.Utils import validate_file_extension, content_file_name_for_result


class TranslateResult(models.Model):
    o_id = models.CharField(max_length=15)
    ord_file = models.FileField(upload_to=content_file_name_for_result, validators=[validate_file_extension])
