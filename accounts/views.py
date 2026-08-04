from django.contrib import messages
from django.contrib.auth import login
from django.contrib.auth.mixins import LoginRequiredMixin
from django.core.exceptions import PermissionDenied
from django.shortcuts import get_object_or_404, redirect
from django.urls import reverse_lazy
from django.views import View
from django.views.generic import CreateView, ListView, UpdateView

from .forms import SignupForm, UserRoleForm
from .models import User


class RoleRequiredMixin(LoginRequiredMixin):
    """Restrict a view to specific roles.

    Authentication is always checked first (via LoginRequiredMixin's
    dispatch), so anonymous users are redirected to the login page —
    never shown a 403. Only once we know the user is authenticated do
    we check their role, and raise PermissionDenied if they don't
    belong to `allowed_roles`.
    """
    allowed_roles = ()

    def dispatch(self, request, *args, **kwargs):
        if not request.user.is_authenticated:
            return self.handle_no_permission()
        if self.allowed_roles and request.user.role not in self.allowed_roles:
            raise PermissionDenied('You do not have permission to access this page.')
        return super().dispatch(request, *args, **kwargs)


class SignupView(CreateView):
    model = User
    form_class = SignupForm
    template_name = 'registration/signup.html'
    success_url = reverse_lazy('post-login-redirect')

    def form_valid(self, form):
        response = super().form_valid(form)
        login(self.request, self.object)
        messages.success(self.request, f'Welcome, {self.object.username}! Your account has been created.')
        return response


class PostLoginRedirectView(LoginRequiredMixin, View):
    """Sends the user to the dashboard — a single entry point that the
    dashboard template itself then renders differently per role."""

    def get(self, request, *args, **kwargs):
        return redirect('dashboard')


class UserListView(RoleRequiredMixin, ListView):
    allowed_roles = (User.Role.ADMIN,)
    model = User
    template_name = 'accounts/user_list.html'
    context_object_name = 'users'
    paginate_by = 15

    def get_queryset(self):
        return User.objects.all().order_by('username')


class UserRoleUpdateView(RoleRequiredMixin, UpdateView):
    allowed_roles = (User.Role.ADMIN,)
    model = User
    form_class = UserRoleForm
    template_name = 'accounts/user_form.html'
    success_url = reverse_lazy('user-list')

    def form_valid(self, form):
        messages.success(self.request, f'Updated role for {self.object.username}.')
        return super().form_valid(form)
