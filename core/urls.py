from django.urls import path

from . import views

urlpatterns = [
    path('dashboard/', views.DashboardView.as_view(), name='dashboard'),

    path('products/', views.ProductListView.as_view(), name='product-list'),
    path('products/new/', views.ProductCreateView.as_view(), name='product-create'),
    path('products/<int:pk>/', views.ProductDetailView.as_view(), name='product-detail'),
    path('products/<int:pk>/edit/', views.ProductUpdateView.as_view(), name='product-update'),
    path('products/<int:pk>/delete/', views.ProductDeleteView.as_view(), name='product-delete'),

    path('boxes/', views.BoxListView.as_view(), name='box-list'),
    path('boxes/new/', views.BoxCreateView.as_view(), name='box-create'),
    path('boxes/<int:pk>/', views.BoxDetailView.as_view(), name='box-detail'),
    path('boxes/<int:pk>/edit/', views.BoxUpdateView.as_view(), name='box-update'),
    path('boxes/<int:pk>/delete/', views.BoxDeleteView.as_view(), name='box-delete'),

    path('orders/', views.OrderListView.as_view(), name='order-list'),
    path('orders/new/', views.OrderCreateView.as_view(), name='order-create'),
    path('orders/<int:pk>/', views.OrderDetailView.as_view(), name='order-detail'),
    path('orders/<int:pk>/edit/', views.OrderUpdateView.as_view(), name='order-update'),
    path('orders/<int:pk>/delete/', views.OrderDeleteView.as_view(), name='order-delete'),
]
