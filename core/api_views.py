from rest_framework import permissions, viewsets

from .ai_service import explain_recommendation
from .models import Box, Order, Product
from .serializers import BoxSerializer, OrderSerializer, ProductSerializer
from .services import recommend_box_for_products


class ProductViewSet(viewsets.ModelViewSet):
    queryset = Product.objects.all()
    serializer_class = ProductSerializer
    permission_classes = [permissions.IsAuthenticated]
    filterset_fields = []
    search_fields = ['name']


class BoxViewSet(viewsets.ModelViewSet):
    queryset = Box.objects.all()
    serializer_class = BoxSerializer
    permission_classes = [permissions.IsAuthenticated]


class OrderViewSet(viewsets.ModelViewSet):
    queryset = Order.objects.all()
    serializer_class = OrderSerializer
    permission_classes = [permissions.IsAuthenticated]

    def perform_create(self, serializer):
        order = serializer.save(created_by=self.request.user)
        best_box = recommend_box_for_products(order.products.all(), Box.objects.all())
        order.recommended_box = best_box
        order.ai_explanation = explain_recommendation(order.products.all(), best_box)
        order.save()
