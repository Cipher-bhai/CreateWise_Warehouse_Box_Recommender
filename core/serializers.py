from rest_framework import serializers

from .models import Box, Order, Product


class ProductSerializer(serializers.ModelSerializer):
    class Meta:
        model = Product
        fields = '__all__'


class BoxSerializer(serializers.ModelSerializer):
    class Meta:
        model = Box
        fields = '__all__'


class OrderSerializer(serializers.ModelSerializer):
    recommended_box_name = serializers.CharField(source='recommended_box.name', read_only=True, default=None)

    class Meta:
        model = Order
        fields = [
            'id', 'customer_name', 'created_at', 'updated_at', 'products',
            'recommended_box', 'recommended_box_name', 'status', 'ai_explanation', 'created_by',
        ]
        read_only_fields = ['recommended_box', 'ai_explanation', 'created_by']
