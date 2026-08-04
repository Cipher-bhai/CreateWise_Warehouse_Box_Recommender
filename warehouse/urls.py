"""warehouse URL Configuration"""
from django.contrib import admin
from django.urls import path, include
from rest_framework.routers import DefaultRouter

from core.api_views import ProductViewSet, BoxViewSet, OrderViewSet
from core import views as core_views

router = DefaultRouter()
router.register('products', ProductViewSet, basename='api-product')
router.register('boxes', BoxViewSet, basename='api-box')
router.register('orders', OrderViewSet, basename='api-order')

urlpatterns = [
    path('admin/', admin.site.urls),
    path('', core_views.LandingView.as_view(), name='landing'),

    path('accounts/', include('accounts.urls')),
    path('', include('core.urls')),

    path('api/', include(router.urls)),
    path('api-auth/', include('rest_framework.urls')),
]
