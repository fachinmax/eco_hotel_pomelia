from django.db import models
from django.contrib.auth.models import AbstractUser


# Create your models here.
# Oggetto user con maggiori informazioni.
class User(AbstractUser):
    ip_address = models.CharField(max_length=15, default=False)
    login_date = models.DateTimeField(auto_now=True)

    def set_ip_address(self, ip):
        self.ip_address = ip
        self.save()

    def get_ip_address(self):
        return self.ip_address

