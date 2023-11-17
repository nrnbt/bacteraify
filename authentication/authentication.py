from django.contrib.auth.backends import ModelBackend
from .models import UserAuth

class EmailBackend(ModelBackend):
    def authenticate(self, request, username=None, password=None, **kwargs):
        try:
            user = UserAuth.objects.get(email=username)
            if user.check_password(password):
                return user
        except UserAuth.DoesNotExist:
            return None

    def get_user(self, user_id):
        try:
            return UserAuth.objects.get(pk=user_id)
        except UserAuth.DoesNotExist:
            return None
