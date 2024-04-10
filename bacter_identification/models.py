from django.db import models
from django.utils import timezone
from django.core.exceptions import ValidationError
import re
import random
import string

def validate_alpha_numeric(value):
    pattern = r'^[A-Z]{2}\d{8}$'
    if not re.match(pattern, value):
        raise ValidationError('Value must start with 2 alphabetic characters followed by 8 digits.')
    
class Survey(models.Model):
    userId = models.IntegerField()
    userEmail = models.EmailField()
    surveyNumber = models.CharField(max_length=10, validators=[validate_alpha_numeric], unique=True)
    patientHash = models.CharField(max_length=255, default=None)
    surveyFileName = models.CharField(max_length=255)
    cnnPredFileName = models.CharField(max_length=255, default=None, null=True)
    svmPredFileName = models.CharField(max_length=255, default=None, null=True)
    rnnPredFileName = models.CharField(max_length=255, default=None, null=True)
    rowNumber = models.IntegerField()
    status = models.CharField(max_length=50)
    created_at = models.DateTimeField(default=timezone.now)
    modelTypes = models.JSONField(default=dict)
    def save(self, *args, **kwargs):
            if not self.surveyNumber:
                is_unique = False
                while not is_unique:
                    new_value = ''.join(random.choices(string.ascii_uppercase, k=2)) + ''.join(random.choices(string.digits, k=8))
                    if not Survey.objects.filter(surveyNumber=new_value).exists():
                        self.surveyNumber = new_value
                        is_unique = True
            super(Survey, self).save(*args, **kwargs)


class Bacteria(models.Model):
    label = models.CharField(max_length=100)
    spectrum = models.TextField()