# from django.contrib.auth.backends import ModelBackend
# from .models import UserAuth

# class EmailBackend(ModelBackend):
#     def authenticate(self, request, username=None, email=None, password=None, **kwargs):
#         try:
#             if email is None:
#                 user = UserAuth.objects.get(username=username)
#                 if user.check_password(password):
#                     return user
#             else:
#                 user = UserAuth.objects.get(email=email)
#                 if user.check_password(password):
#                     return user
#         except UserAuth.DoesNotExist:
#             return None

#     def get_user(self, user_id):
#         try:
#             return UserAuth.objects.get(pk=user_id)
#         except UserAuth.DoesNotExist:
#             return None
