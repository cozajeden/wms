from users.models import Company
from clients.models import Client
from django.db import models


class Order(models.Model):
    company = models.ForeignKey(Company, on_delete=models.CASCADE)
    STATUS_CHOICES = (
        ('Draft', 'Draft'),
        ('Confirmed', 'Confirmed'),
        ('Shipped', 'Shipped'),
        ('Delivered', 'Delivered'),
        ('Cancelled', 'Cancelled'),
    )
    status = models.CharField(max_length=20, choices=STATUS_CHOICES, default='Draft')
    order_date = models.DateTimeField(auto_now_add=True)
    shipped_date = models.DateTimeField(null=True, blank=True)
    delivered_date = models.DateTimeField(null=True, blank=True)
    client = models.ForeignKey(Client, on_delete=models.CASCADE)

    def __str__(self):
        return f'Order: {self.id} - {self.status}'

    class Meta:
        db_table = 'order'
