import random
import string
from django.contrib.auth.models import User
from django.db import models


class ConfirmationCode(models.Model):
    user = models.OneToOneField(User, on_delete=models.CASCADE, related_name='confirmation_code')
    code = models.CharField(max_length=6)
    created_at = models.DateTimeField(auto_now_add=True)

    def __str__(self):
        return f'{self.user.username} - {self.code}'

    @staticmethod
    def generate_code():
        return ''.join(random.choices(string.digits, k=6))