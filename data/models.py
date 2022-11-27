from django.db import models


# Create your models here.
class Data(models.Model):
    hash_transaction = models.CharField(max_length=66)

    def set_hash_transaction(self, hash):
        self.hash_transaction = hash
        self.save()

    def get_hash_transaction(self):
        return self.hash_transaction
