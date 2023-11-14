from django.contrib.auth.models import AbstractUser
from django.db import models

class UserAuth(AbstractUser):
    corporateId = models.CharField(max_length=100, blank=True)
