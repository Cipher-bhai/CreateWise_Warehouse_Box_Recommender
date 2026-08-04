from django.test import TestCase
from django.urls import reverse

from .models import User


class UserModelTests(TestCase):
    def test_default_role_is_staff(self):
        user = User.objects.create_user(username='alice', password='pass12345')
        self.assertEqual(user.role, User.Role.STAFF)
        self.assertTrue(user.is_staff_role)
        self.assertFalse(user.can_manage_catalog())
        self.assertFalse(user.can_manage_users())

    def test_admin_role_permissions(self):
        user = User.objects.create_user(username='admin1', password='pass12345', role=User.Role.ADMIN)
        self.assertTrue(user.can_manage_catalog())
        self.assertTrue(user.can_manage_users())

    def test_manager_role_permissions(self):
        user = User.objects.create_user(username='mgr1', password='pass12345', role=User.Role.MANAGER)
        self.assertTrue(user.can_manage_catalog())
        self.assertFalse(user.can_manage_users())

    def test_str_representation(self):
        user = User.objects.create_user(username='bob', password='pass12345', role=User.Role.MANAGER)
        self.assertIn('bob', str(user))
        self.assertIn('Manager', str(user))


class SignupTests(TestCase):
    def test_signup_creates_staff_user_and_logs_in(self):
        response = self.client.post(reverse('signup'), {
            'username': 'newstaff',
            'email': 'newstaff@example.com',
            'first_name': 'New',
            'last_name': 'Staff',
            'password1': 'ComplexPass123!',
            'password2': 'ComplexPass123!',
        })
        self.assertEqual(response.status_code, 302)
        user = User.objects.get(username='newstaff')
        self.assertEqual(user.role, User.Role.STAFF)
        # Should already be logged in after signup.
        response = self.client.get(reverse('dashboard'))
        self.assertEqual(response.status_code, 200)

    def test_signup_ignores_role_field_if_submitted(self):
        """A malicious signup payload trying to self-promote to admin
        must be ignored — SignupForm always forces STAFF."""
        self.client.post(reverse('signup'), {
            'username': 'sneaky',
            'email': 'sneaky@example.com',
            'password1': 'ComplexPass123!',
            'password2': 'ComplexPass123!',
            'role': 'admin',
        })
        user = User.objects.get(username='sneaky')
        self.assertEqual(user.role, User.Role.STAFF)


class RoleRequiredMixinTests(TestCase):
    """Anonymous users must be redirected to login (302), never 403 —
    this covers the login-redirect regression from the original build."""

    def setUp(self):
        self.admin = User.objects.create_user(username='admin2', password='pass12345', role=User.Role.ADMIN)
        self.staff = User.objects.create_user(username='staffer', password='pass12345', role=User.Role.STAFF)

    def test_anonymous_user_redirected_to_login_not_403(self):
        response = self.client.get(reverse('user-list'))
        self.assertEqual(response.status_code, 302)
        self.assertIn(reverse('login'), response.url)

    def test_non_admin_gets_403_on_user_list(self):
        self.client.login(username='staffer', password='pass12345')
        response = self.client.get(reverse('user-list'))
        self.assertEqual(response.status_code, 403)

    def test_admin_can_access_user_list(self):
        self.client.login(username='admin2', password='pass12345')
        response = self.client.get(reverse('user-list'))
        self.assertEqual(response.status_code, 200)
