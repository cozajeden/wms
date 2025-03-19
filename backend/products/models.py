from django.core.validators import MinValueValidator
from users.models import CustomUser, Company
from warehouse.models import Warehouse
from suppliers.models import Supplier
from orders.models import Order
from django.db import models


class Material(models.Model):
    company = models.ForeignKey(Company, on_delete=models.CASCADE)
    name = models.CharField(max_length=100, unique=True)
    unit = models.CharField(max_length=20)

    def __str__(self):
        return f'Material: {self.name}'

    class Meta:
        db_table = 'material'


class Product(models.Model):
    company = models.ForeignKey(Company, on_delete=models.CASCADE)
    name = models.CharField(max_length=100, unique=True)
    unit = models.CharField(max_length=20)

    def __str__(self):
        return f'Product: {self.name}'

    class Meta:
        db_table = 'product'


class BillOfMaterials(models.Model):
    product = models.ForeignKey(Product, on_delete=models.CASCADE)
    material = models.ForeignKey(Material, on_delete=models.CASCADE)
    quantity = models.FloatField(validators=[MinValueValidator(0)])

    def __str__(self):
        return f'BOM: {self.product} - {self.material} - {self.quantity}'

    class Meta:
        db_table = 'bom'
        unique_together = ('product', 'material')


class Lot(models.Model):
    supplier = models.ForeignKey(Supplier, on_delete=models.CASCADE)
    material = models.ForeignKey(Material, on_delete=models.CASCADE)
    quantity_received = models.FloatField(validators=[MinValueValidator(0)])
    quantity_remaining = models.FloatField(validators=[MinValueValidator(0)])
    received = models.DateTimeField(auto_now_add=True)
    expiration = models.DateTimeField()

    def __str__(self):
        return f'Lot: {self.material} - {self.quantity_remaining}'

    class Meta:
        db_table = 'lot'


class Inventory(models.Model):
    warehouse = models.ForeignKey(Warehouse, on_delete=models.CASCADE)
    lot = models.ForeignKey(Lot, on_delete=models.CASCADE)
    quantity = models.FloatField(validators=[MinValueValidator(0)])

    def __str__(self):
        return f'Inventory: {self.warehouse} - {self.lot} - {self.quantity}'

    class Meta:
        db_table = 'inventory'
        unique_together = ('warehouse', 'lot')


class ProductBatch(models.Model):
    warehouse = models.ForeignKey(Warehouse, on_delete=models.CASCADE)
    product = models.ForeignKey(Product, on_delete=models.CASCADE)
    order = models.ForeignKey(Order, on_delete=models.CASCADE)
    ordered_quantity = models.FloatField(validators=[MinValueValidator(0)])
    produced_quantity = models.FloatField(validators=[MinValueValidator(0)])
    lots = models.ManyToManyField(Lot, through='Batch')

    def __str__(self):
        return f'Batch: {self.product} - {self.order} - {self.produced_quantity}/{self.ordered_quantity}'

    class Meta:
        db_table = 'product_batch'


class Batch(models.Model):
    product_batch = models.ForeignKey(ProductBatch, on_delete=models.CASCADE)
    lot = models.ForeignKey(Lot, on_delete=models.CASCADE)
    quantity = models.FloatField(validators=[MinValueValidator(0)])

    def __str__(self):
        return f'Batch: {self.product_batch} - {self.lot} - {self.quantity}'

    class Meta:
        db_table = 'batch'
        unique_together = ('product_batch', 'lot')


class Item(models.Model):
    serial_number = models.CharField(max_length=100, unique=True)
    batch = models.ForeignKey(ProductBatch, on_delete=models.CASCADE)
    operator = models.ForeignKey(CustomUser, on_delete=models.CASCADE)
    production_date = models.DateTimeField(auto_now_add=True)

    def __str__(self):
        return f'Item: {self.serial_number}'

    class Meta:
        db_table = 'item'
        unique_together = ('serial_number', 'batch')
