from django.conf import settings
from decimal import Decimal

from django.core.validators import MinValueValidator
from django.db import models
from django.urls import reverse


class Product(models.Model):
    name = models.CharField(max_length=200)
    length = models.DecimalField(max_digits=6, decimal_places=2, validators=[MinValueValidator(Decimal('0.01'))],
                                  help_text='Length in cm')
    width = models.DecimalField(max_digits=6, decimal_places=2, validators=[MinValueValidator(Decimal('0.01'))],
                                 help_text='Width in cm')
    height = models.DecimalField(max_digits=6, decimal_places=2, validators=[MinValueValidator(Decimal('0.01'))],
                                  help_text='Height in cm')
    weight = models.DecimalField(max_digits=6, decimal_places=2, validators=[MinValueValidator(Decimal('0.01'))],
                                  help_text='Weight in kg')
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    class Meta:
        ordering = ['name']

    def volume(self):
        return self.length * self.width * self.height

    def get_absolute_url(self):
        return reverse('product-detail', kwargs={'pk': self.pk})

    def __str__(self):
        return self.name


class Box(models.Model):
    name = models.CharField(max_length=200)
    length = models.DecimalField(max_digits=6, decimal_places=2, validators=[MinValueValidator(Decimal('0.01'))],
                                  help_text='Interior length in cm')
    width = models.DecimalField(max_digits=6, decimal_places=2, validators=[MinValueValidator(Decimal('0.01'))],
                                 help_text='Interior width in cm')
    height = models.DecimalField(max_digits=6, decimal_places=2, validators=[MinValueValidator(Decimal('0.01'))],
                                  help_text='Interior height in cm')
    max_weight = models.DecimalField(max_digits=6, decimal_places=2, validators=[MinValueValidator(Decimal('0.01'))],
                                      help_text='Maximum weight capacity in kg')
    cost = models.DecimalField(max_digits=8, decimal_places=2, validators=[MinValueValidator(Decimal('0'))],
                                help_text='Cost of this box')
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    class Meta:
        ordering = ['cost']

    def volume(self):
        return self.length * self.width * self.height

    def get_absolute_url(self):
        return reverse('box-detail', kwargs={'pk': self.pk})

    def __str__(self):
        return self.name


class Order(models.Model):
    class Status(models.TextChoices):
        PENDING = 'pending', 'Pending'
        PACKED = 'packed', 'Packed'
        SHIPPED = 'shipped', 'Shipped'

    customer_name = models.CharField(max_length=200)
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)
    products = models.ManyToManyField(Product, related_name='orders')
    recommended_box = models.ForeignKey(Box, null=True, blank=True, on_delete=models.SET_NULL,
                                         related_name='orders')
    status = models.CharField(max_length=20, choices=Status.choices, default=Status.PENDING)
    ai_explanation = models.TextField(blank=True, default='',
                                       help_text='AI-generated explanation of why the box was recommended.')
    created_by = models.ForeignKey(settings.AUTH_USER_MODEL, null=True, blank=True,
                                    on_delete=models.SET_NULL, related_name='orders_created')

    class Meta:
        ordering = ['-created_at']

    def get_absolute_url(self):
        return reverse('order-detail', kwargs={'pk': self.pk})

    def __str__(self):
        return f'Order #{self.id} - {self.customer_name}'
