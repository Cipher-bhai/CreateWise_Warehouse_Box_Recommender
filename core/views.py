import json

from django.contrib import messages
from django.contrib.auth.mixins import LoginRequiredMixin
from django.db.models import Count
from django.http import HttpResponseRedirect
from django.urls import reverse_lazy
from django.views.generic import (
    CreateView, DeleteView, DetailView, ListView, TemplateView, UpdateView,
)

from accounts.models import User
from accounts.views import RoleRequiredMixin

from .forms import BoxForm, OrderForm, ProductForm
from .models import Box, Order, Product
from .services import recommend_box_for_products
from .ai_service import explain_recommendation

CATALOG_ROLES = (User.Role.ADMIN, User.Role.MANAGER)


class LandingView(TemplateView):
    template_name = 'landing.html'


class DashboardView(LoginRequiredMixin, TemplateView):
    """Renders one template, but the data — and therefore what's on
    screen — is scoped to the signed-in user's role:

      Admin   — full warehouse-wide stats & charts, plus a Users panel.
      Manager — full warehouse-wide stats & charts, no user management.
      Staff   — only their own orders: a personal order count, a
                personal status chart, and their own recent orders —
                nothing about other staff members' activity.
    """
    template_name = 'dashboard/dashboard.html'

    def get_context_data(self, **kwargs):
        ctx = super().get_context_data(**kwargs)
        user = self.request.user

        ctx['is_admin'] = user.role == User.Role.ADMIN
        ctx['is_manager'] = user.role == User.Role.MANAGER
        ctx['is_staff_role'] = user.role == User.Role.STAFF
        ctx['product_count'] = Product.objects.count()
        ctx['box_count'] = Box.objects.count()

        if user.can_manage_catalog():
            # Admin & Manager: warehouse-wide view.
            orders = Order.objects.all()
            ctx['order_count'] = orders.count()
            ctx['orders_heading'] = 'Latest orders'
            if ctx['is_admin']:
                ctx['user_count'] = User.objects.count()
        else:
            # Staff: scoped to their own orders only.
            orders = Order.objects.filter(created_by=user)
            ctx['order_count'] = orders.count()
            ctx['orders_heading'] = 'My recent orders'

        ctx['latest_orders'] = orders.select_related('recommended_box').order_by('-created_at')[:5]

        status_counts = orders.values('status').annotate(total=Count('id'))
        status_labels = [Order.Status(row['status']).label for row in status_counts]
        status_totals = [row['total'] for row in status_counts]
        ctx['status_chart_labels'] = json.dumps(status_labels)
        ctx['status_chart_data'] = json.dumps(status_totals)

        box_usage = (
            orders.exclude(recommended_box__isnull=True)
            .values('recommended_box__name')
            .annotate(total=Count('id'))
            .order_by('-total')[:6]
        )
        ctx['box_chart_labels'] = json.dumps([row['recommended_box__name'] for row in box_usage])
        ctx['box_chart_data'] = json.dumps([row['total'] for row in box_usage])

        return ctx


# ---------------------------------------------------------------------------
# Product CRUD
# ---------------------------------------------------------------------------
class ProductListView(LoginRequiredMixin, ListView):
    model = Product
    paginate_by = 10
    template_name = 'products/product_list.html'

    def get_queryset(self):
        qs = super().get_queryset()
        q = self.request.GET.get('q')
        if q:
            qs = qs.filter(name__icontains=q)
        return qs


class ProductDetailView(LoginRequiredMixin, DetailView):
    model = Product
    template_name = 'products/product_detail.html'


class ProductCreateView(RoleRequiredMixin, CreateView):
    allowed_roles = CATALOG_ROLES
    model = Product
    form_class = ProductForm
    template_name = 'products/product_form.html'
    success_url = reverse_lazy('product-list')

    def form_valid(self, form):
        messages.success(self.request, f'Product "{form.instance.name}" created.')
        return super().form_valid(form)


class ProductUpdateView(RoleRequiredMixin, UpdateView):
    allowed_roles = CATALOG_ROLES
    model = Product
    form_class = ProductForm
    template_name = 'products/product_form.html'
    success_url = reverse_lazy('product-list')

    def form_valid(self, form):
        messages.success(self.request, f'Product "{form.instance.name}" updated.')
        return super().form_valid(form)


class ProductDeleteView(RoleRequiredMixin, DeleteView):
    allowed_roles = CATALOG_ROLES
    model = Product
    template_name = 'products/product_confirm_delete.html'
    success_url = reverse_lazy('product-list')


# ---------------------------------------------------------------------------
# Box CRUD
# ---------------------------------------------------------------------------
class BoxListView(LoginRequiredMixin, ListView):
    model = Box
    paginate_by = 10
    template_name = 'boxes/box_list.html'

    def get_queryset(self):
        qs = super().get_queryset()
        q = self.request.GET.get('q')
        if q:
            qs = qs.filter(name__icontains=q)
        return qs


class BoxDetailView(LoginRequiredMixin, DetailView):
    model = Box
    template_name = 'boxes/box_detail.html'


class BoxCreateView(RoleRequiredMixin, CreateView):
    allowed_roles = CATALOG_ROLES
    model = Box
    form_class = BoxForm
    template_name = 'boxes/box_form.html'
    success_url = reverse_lazy('box-list')

    def form_valid(self, form):
        messages.success(self.request, f'Box "{form.instance.name}" created.')
        return super().form_valid(form)


class BoxUpdateView(RoleRequiredMixin, UpdateView):
    allowed_roles = CATALOG_ROLES
    model = Box
    form_class = BoxForm
    template_name = 'boxes/box_form.html'
    success_url = reverse_lazy('box-list')

    def form_valid(self, form):
        messages.success(self.request, f'Box "{form.instance.name}" updated.')
        return super().form_valid(form)


class BoxDeleteView(RoleRequiredMixin, DeleteView):
    allowed_roles = CATALOG_ROLES
    model = Box
    template_name = 'boxes/box_confirm_delete.html'
    success_url = reverse_lazy('box-list')


# ---------------------------------------------------------------------------
# Order CRUD (creation triggers the recommendation algorithm + AI explanation)
# ---------------------------------------------------------------------------
class OrderListView(LoginRequiredMixin, ListView):
    model = Order
    paginate_by = 10
    template_name = 'orders/order_list.html'

    def get_queryset(self):
        qs = super().get_queryset().select_related('recommended_box').prefetch_related('products')
        q = self.request.GET.get('q')
        if q:
            qs = qs.filter(customer_name__icontains=q)
        status = self.request.GET.get('status')
        if status:
            qs = qs.filter(status=status)
        return qs

    def get_context_data(self, **kwargs):
        ctx = super().get_context_data(**kwargs)
        ctx['status_choices'] = Order.Status.choices
        return ctx


class OrderDetailView(LoginRequiredMixin, DetailView):
    model = Order
    template_name = 'orders/order_detail.html'


class OrderCreateView(LoginRequiredMixin, CreateView):
    """Any authenticated role (including Staff) can create orders — this
    is the core day-to-day task of the app."""
    model = Order
    form_class = OrderForm
    template_name = 'orders/order_form.html'

    def form_valid(self, form):
        self.object = form.save(commit=False)
        self.object.created_by = self.request.user
        self.object.save()
        form.save_m2m()

        boxes = Box.objects.all()
        best_box = recommend_box_for_products(self.object.products.all(), boxes)
        self.object.recommended_box = best_box
        self.object.ai_explanation = explain_recommendation(self.object.products.all(), best_box)
        self.object.save()

        if best_box:
            messages.success(self.request, f'Order created — recommended box: {best_box.name}.')
        else:
            messages.warning(self.request, 'Order created, but no box in the catalog fits this shipment.')
        return HttpResponseRedirect(self.get_success_url())

    def get_success_url(self):
        return self.object.get_absolute_url()


class OrderUpdateView(RoleRequiredMixin, UpdateView):
    allowed_roles = CATALOG_ROLES
    model = Order
    form_class = OrderForm
    template_name = 'orders/order_form.html'

    def form_valid(self, form):
        response = super().form_valid(form)
        boxes = Box.objects.all()
        best_box = recommend_box_for_products(self.object.products.all(), boxes)
        self.object.recommended_box = best_box
        self.object.ai_explanation = explain_recommendation(self.object.products.all(), best_box)
        self.object.save()
        messages.success(self.request, f'Order #{self.object.pk} updated.')
        return response

    def get_success_url(self):
        return self.object.get_absolute_url()


class OrderDeleteView(RoleRequiredMixin, DeleteView):
    allowed_roles = CATALOG_ROLES
    model = Order
    template_name = 'orders/order_confirm_delete.html'
    success_url = reverse_lazy('order-list')
