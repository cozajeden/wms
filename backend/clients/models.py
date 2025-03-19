from users.models import Company
from django.db import models


class Client(models.Model):
    company = models.ForeignKey(Company, on_delete=models.CASCADE)
    name = models.CharField(max_length=100)
    address = models.CharField(max_length=100)
    phone = models.CharField(max_length=20)
    email = models.EmailField()
    website = models.URLField()

    def __str__(self):
        return f'Client: {self.name}'

    class Meta:
        db_table = 'client'
        unique_together = ('name', 'email')
