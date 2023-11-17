from django.db import models
from django.utils import timezone

class Survey(models.Model):
    userId = models.IntegerField()
    userEmail = models.EmailField()
    surveyFileName = models.CharField(max_length=255)
    resultFileName = models.CharField(max_length=255)
    rowNumber = models.IntegerField()
    type = models.CharField(max_length=50)
    created_at = models.DateTimeField(default=timezone.now)