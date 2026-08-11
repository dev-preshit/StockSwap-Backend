from django.db import models
from django.contrib.auth.models import User

class Shop(models.Model):
    user = models.OneToOneField(User, on_delete=models.CASCADE, related_name='shop')
    shop_name = models.CharField(max_length=255)
    phone = models.CharField(max_length=50)
    address = models.TextField(blank=True, default='')
    created_at = models.DateTimeField(auto_now_add=True)

    def __str__(self):
        return f"{self.shop_name} ({self.user.email})"
