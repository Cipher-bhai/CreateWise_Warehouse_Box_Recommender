from django.contrib import admin

from .models import Box, Order, Product


@admin.register(Product)
class ProductAdmin(admin.ModelAdmin):
    list_display = ('name', 'length', 'width', 'height', 'weight')
    search_fields = ('name',)


@admin.register(Box)
class BoxAdmin(admin.ModelAdmin):
    list_display = ('name', 'length', 'width', 'height', 'max_weight', 'cost')
    search_fields = ('name',)
    ordering = ('cost',)


@admin.register(Order)
class OrderAdmin(admin.ModelAdmin):
    list_display = ('id', 'customer_name', 'status', 'recommended_box', 'created_at')
    list_filter = ('status',)
    search_fields = ('customer_name',)
    filter_horizontal = ('products',)
