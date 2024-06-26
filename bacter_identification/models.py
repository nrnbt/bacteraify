from django.db import models
from django.utils import timezone
from django.core.exceptions import ValidationError
import re
import random
import string

def validate_alpha_numeric(value):
    pattern = r'^[A-Za-z]{2}\d{8}$'
    if not re.match(pattern, value):
        raise ValidationError('Value must start with 2 alphabetic characters followed by 8 digits.')
    
class Survey(models.Model):
    userId = models.IntegerField()
    userEmail = models.EmailField()
    number = models.CharField(max_length=10, validators=[validate_alpha_numeric], unique=True)
    userHash = models.CharField(max_length=255, default=None)
    surveyFileName = models.CharField(max_length=255)
    resultFileName = models.CharField(max_length=255)
    rowNumber = models.IntegerField()
    type = models.CharField(max_length=50)
    created_at = models.DateTimeField(default=timezone.now)
    def save(self, *args, **kwargs):
            if not self.number:
                is_unique = False
                while not is_unique:
                    new_value = ''.join(random.choices(string.ascii_letters, k=2)) + ''.join(random.choices(string.digits, k=8))
                    if not Survey.objects.filter(number=new_value).exists():
                        self.number = new_value
                        is_unique = True
            super(Survey, self).save(*args, **kwargs)


class Bacteria(models.Model):
    label = models.CharField(max_length=100)
    spectrum = models.TextField()