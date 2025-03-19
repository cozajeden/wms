from django.db import models
from users import models as users_models


class Warehouse(models.Model):
    company = models.ForeignKey(users_models.Company, on_delete=models.CASCADE)
    NAME_CHOICES = (
        ('Main', 'Main'),
        ('Production', 'Production'),
        ('Finished', 'Finished'),
        ('Shipped', 'Shipped'),
    )
    name = models.CharField(max_length=20, choices=NAME_CHOICES)

    def __str__(self):
        return f'Warehouse: {self.name} - {self.name}'

    class Meta:
        db_table = 'warehouse'
        unique_together = ('company', 'name')
