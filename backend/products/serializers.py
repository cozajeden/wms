from rest_framework import serializers
from drf_yasg import openapi
from . import models


class MaterialSerializer(serializers.ModelSerializer):
    class Meta:
        model = models.Material
        fields = ['name', 'unit']
    
    def create(self, validated_data):
        validated_data['company'] = self.context['request'].user.company
        return super().create(validated_data)


class ProductSerializer(serializers.ModelSerializer):
    class Meta:
        model = models.Product
        fields = '__all__'


class BillOfMaterialsSerializer(serializers.ModelSerializer):
    class Meta:
        model = models.BillOfMaterials
        fields = '__all__'


class LotSerializer(serializers.ModelSerializer):
    class Meta:
        model = models.Lot
        fields = '__all__'


class InventorySerializer(serializers.ModelSerializer):
    class Meta:
        model = models.Inventory
        fields = '__all__'


class ProductBatchSerializer(serializers.ModelSerializer):
    class Meta:
        model = models.ProductBatch
        fields = '__all__'



class BatchSerializer(serializers.ModelSerializer):
    class Meta:
        model = models.Batch
        fields = '__all__'



class ItemSerializer(serializers.ModelSerializer):
    class Meta:
        model = models.Item
        fields = '__all__'
