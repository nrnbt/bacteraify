from django.contrib.auth.backends import ModelBackend
from authentication.models import MerchantAdmin, MerchantEmployee

class MerchAdminEmailBackend(ModelBackend):
  def authenticate(self, request, email=None, password=None, **kwargs):
    try:
      user = MerchantAdmin.objects.get(email=email)
      if user.check_password(password):
          return user
    except MerchantAdmin.DoesNotExist:
      return
  
  def get_user(self, user_id):
    try:
        return MerchantAdmin.objects.get(pk=user_id)
    except MerchantAdmin.DoesNotExist:
        return None

class MerchantEmployeeEmailBackend(ModelBackend):
  def authenticate(self, request, email=None, password=None, **kwargs):
    try:
      user = MerchantEmployee.objects.get(email=email)
      if user.check_password(password):
          return user
    except MerchantEmployee.DoesNotExist:
      return
    
  def get_user(self, user_id):
        try:
            return MerchantEmployee.objects.get(pk=user_id)
        except MerchantEmployee.DoesNotExist:
            return None

