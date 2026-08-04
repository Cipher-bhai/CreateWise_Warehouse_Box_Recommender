from django.contrib.auth.models import AbstractUser
from django.db import models


class User(AbstractUser):
    """Custom user model with a warehouse role.

    Roles:
      ADMIN   — full access, including user management.
      MANAGER — full CRUD on products/boxes/orders, no user management.
      STAFF   — can view products/boxes and create/manage orders only.
    """

    class Role(models.TextChoices):
        ADMIN = 'admin', 'Admin'
        MANAGER = 'manager', 'Manager'
        STAFF = 'staff', 'Staff'

    role = models.CharField(
        max_length=20,
        choices=Role.choices,
        default=Role.STAFF,
        help_text='Controls which parts of the app this user can access.',
    )

    @property
    def is_admin_role(self):
        return self.role == self.Role.ADMIN

    @property
    def is_manager_role(self):
        return self.role == self.Role.MANAGER

    @property
    def is_staff_role(self):
        return self.role == self.Role.STAFF

    def can_manage_catalog(self):
        """Admins and managers can create/edit/delete Products & Boxes."""
        return self.role in (self.Role.ADMIN, self.Role.MANAGER)

    def can_manage_users(self):
        return self.role == self.Role.ADMIN

    def __str__(self):
        return f'{self.username} ({self.get_role_display()})'
