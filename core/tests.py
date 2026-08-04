from decimal import Decimal

from django.test import TestCase
from django.urls import reverse

from accounts.models import User
from .ai_service import explain_recommendation
from .models import Box, Order, Product
from .services import combined_requirements, recommend_box, recommend_box_for_products


# ---------------------------------------------------------------------------
# Model tests
# ---------------------------------------------------------------------------
class ProductModelTests(TestCase):
    def test_volume_and_str(self):
        p = Product.objects.create(name='Widget', length=10, width=10, height=10, weight=1)
        self.assertEqual(p.volume(), Decimal('1000.00'))
        self.assertEqual(str(p), 'Widget')


class BoxModelTests(TestCase):
    def test_volume_and_str(self):
        b = Box.objects.create(name='Small', length=20, width=20, height=20, max_weight=5, cost=10)
        self.assertEqual(b.volume(), Decimal('8000.00'))
        self.assertEqual(str(b), 'Small')


class OrderModelTests(TestCase):
    def test_str(self):
        o = Order.objects.create(customer_name='Jane Doe')
        self.assertIn('Jane Doe', str(o))
        self.assertEqual(o.status, Order.Status.PENDING)


# ---------------------------------------------------------------------------
# recommend_box() — the heart of the app
# ---------------------------------------------------------------------------
class RecommendBoxTests(TestCase):
    def setUp(self):
        self.box_a = Box.objects.create(name='A', length=30, width=30, height=30, max_weight=5, cost=20)
        self.box_b = Box.objects.create(name='B', length=25, width=20, height=15, max_weight=5, cost=18)
        self.box_c = Box.objects.create(name='C', length=50, width=50, height=50, max_weight=5, cost=40)

    def test_lowest_cost_box_wins(self):
        boxes = Box.objects.all()
        best = recommend_box(Decimal(20), Decimal(15), Decimal(10), Decimal(2), boxes)
        self.assertEqual(best, self.box_b)

    def test_weight_limit_excludes_box(self):
        heavy_box = Box.objects.create(name='D', length=25, width=20, height=15, max_weight=1, cost=5)
        boxes = Box.objects.all()
        best = recommend_box(Decimal(20), Decimal(15), Decimal(10), Decimal(2), boxes)
        # box D is cheapest but can't hold 2kg, so it must not be picked
        self.assertNotEqual(best, heavy_box)
        self.assertEqual(best, self.box_b)

    def test_tie_broken_by_smallest_wasted_volume(self):
        Box.objects.all().delete()
        tight = Box.objects.create(name='Tight', length=21, width=16, height=11, max_weight=5, cost=15)
        loose = Box.objects.create(name='Loose', length=40, width=40, height=40, max_weight=5, cost=15)
        boxes = Box.objects.all()
        best = recommend_box(Decimal(20), Decimal(15), Decimal(10), Decimal(2), boxes)
        self.assertEqual(best, tight)

    def test_returns_none_when_nothing_fits(self):
        boxes = Box.objects.filter(name='B')
        best = recommend_box(Decimal(100), Decimal(100), Decimal(100), Decimal(2), boxes)
        self.assertIsNone(best)

    def test_returns_none_for_empty_box_queryset(self):
        best = recommend_box(Decimal(1), Decimal(1), Decimal(1), Decimal(1), Box.objects.none())
        self.assertIsNone(best)


class CombinedRequirementsTests(TestCase):
    def test_combines_multiple_products(self):
        p1 = Product.objects.create(name='P1', length=10, width=5, height=3, weight=1)
        p2 = Product.objects.create(name='P2', length=8, width=6, height=4, weight=2)
        length, width, height, weight = combined_requirements([p1, p2])
        self.assertEqual(length, Decimal('10'))
        self.assertEqual(width, Decimal('6'))
        self.assertEqual(height, Decimal('7'))
        self.assertEqual(weight, Decimal('3'))

    def test_empty_products_returns_none(self):
        self.assertIsNone(combined_requirements([]))

    def test_recommend_box_for_products_end_to_end(self):
        p1 = Product.objects.create(name='P1', length=10, width=5, height=3, weight=1)
        box = Box.objects.create(name='Fits', length=15, width=10, height=10, max_weight=5, cost=10)
        result = recommend_box_for_products([p1], Box.objects.all())
        self.assertEqual(result, box)


# ---------------------------------------------------------------------------
# AI explanation service — must never raise, always returns text
# ---------------------------------------------------------------------------
class AIServiceTests(TestCase):
    def test_fallback_explanation_when_no_api_key(self):
        product = Product.objects.create(name='P', length=5, width=5, height=5, weight=1)
        box = Box.objects.create(name='B', length=10, width=10, height=10, max_weight=5, cost=10)
        text = explain_recommendation([product], box)
        self.assertIn('B', text)
        self.assertIsInstance(text, str)
        self.assertGreater(len(text), 0)

    def test_explanation_when_no_box_found(self):
        product = Product.objects.create(name='P', length=5, width=5, height=5, weight=1)
        text = explain_recommendation([product], None)
        self.assertIsInstance(text, str)
        self.assertIn('No box', text)


# ---------------------------------------------------------------------------
# Auth + CRUD permission tests
# ---------------------------------------------------------------------------
class AuthTests(TestCase):
    def setUp(self):
        self.user = User.objects.create_user(username='joe', password='pass12345', role=User.Role.MANAGER)

    def test_login_logout(self):
        response = self.client.post(reverse('login'), {'username': 'joe', 'password': 'pass12345'})
        self.assertEqual(response.status_code, 302)
        response = self.client.get(reverse('dashboard'))
        self.assertEqual(response.status_code, 200)
        self.client.logout()
        response = self.client.get(reverse('dashboard'))
        self.assertEqual(response.status_code, 302)

    def test_protected_view_redirects_anonymous(self):
        response = self.client.get(reverse('product-list'))
        self.assertEqual(response.status_code, 302)
        self.assertIn(reverse('login'), response.url)


class ProductCRUDPermissionTests(TestCase):
    def setUp(self):
        self.admin = User.objects.create_user(username='admin3', password='pass12345', role=User.Role.ADMIN)
        self.manager = User.objects.create_user(username='mgr2', password='pass12345', role=User.Role.MANAGER)
        self.staff = User.objects.create_user(username='staff2', password='pass12345', role=User.Role.STAFF)
        self.product = Product.objects.create(name='Existing', length=1, width=1, height=1, weight=1)

    def test_staff_can_view_but_not_create_product(self):
        self.client.login(username='staff2', password='pass12345')
        response = self.client.get(reverse('product-list'))
        self.assertEqual(response.status_code, 200)

        response = self.client.get(reverse('product-create'))
        self.assertEqual(response.status_code, 403)

        response = self.client.post(reverse('product-create'), {
            'name': 'New', 'length': 1, 'width': 1, 'height': 1, 'weight': 1,
        })
        self.assertEqual(response.status_code, 403)
        self.assertFalse(Product.objects.filter(name='New').exists())

    def test_manager_can_create_product(self):
        self.client.login(username='mgr2', password='pass12345')
        response = self.client.post(reverse('product-create'), {
            'name': 'Manager Product', 'length': 2, 'width': 2, 'height': 2, 'weight': 2,
        })
        self.assertEqual(response.status_code, 302)
        self.assertTrue(Product.objects.filter(name='Manager Product').exists())

    def test_admin_can_delete_product(self):
        self.client.login(username='admin3', password='pass12345')
        response = self.client.post(reverse('product-delete', kwargs={'pk': self.product.pk}))
        self.assertEqual(response.status_code, 302)
        self.assertFalse(Product.objects.filter(pk=self.product.pk).exists())

    def test_staff_cannot_delete_product(self):
        self.client.login(username='staff2', password='pass12345')
        response = self.client.post(reverse('product-delete', kwargs={'pk': self.product.pk}))
        self.assertEqual(response.status_code, 403)
        self.assertTrue(Product.objects.filter(pk=self.product.pk).exists())


class OrderFlowTests(TestCase):
    """Full order-creation flow: view -> recommend_box() -> AI explanation."""

    def setUp(self):
        self.staff = User.objects.create_user(username='staff3', password='pass12345', role=User.Role.STAFF)
        self.product = Product.objects.create(name='Book', length=20, width=15, height=3, weight=1)
        self.box_cheap = Box.objects.create(name='Mailer', length=25, width=20, height=5, max_weight=5, cost=8)
        self.box_expensive = Box.objects.create(name='Crate', length=50, width=50, height=50, max_weight=5, cost=30)

    def test_staff_can_create_order_and_gets_recommendation(self):
        self.client.login(username='staff3', password='pass12345')
        response = self.client.post(reverse('order-create'), {
            'customer_name': 'Acme Corp',
            'products': [self.product.pk],
        })
        self.assertEqual(response.status_code, 302)
        order = Order.objects.get(customer_name='Acme Corp')
        self.assertEqual(order.recommended_box, self.box_cheap)
        self.assertTrue(order.ai_explanation)
        self.assertEqual(order.created_by, self.staff)

    def test_order_with_no_fitting_box(self):
        Box.objects.all().delete()
        self.client.login(username='staff3', password='pass12345')
        response = self.client.post(reverse('order-create'), {
            'customer_name': 'No Fit Co',
            'products': [self.product.pk],
        })
        self.assertEqual(response.status_code, 302)
        order = Order.objects.get(customer_name='No Fit Co')
        self.assertIsNone(order.recommended_box)

    def test_staff_cannot_delete_order(self):
        order = Order.objects.create(customer_name='Locked')
        self.client.login(username='staff3', password='pass12345')
        response = self.client.post(reverse('order-delete', kwargs={'pk': order.pk}))
        self.assertEqual(response.status_code, 403)


class DashboardTests(TestCase):
    def test_dashboard_renders_with_chart_data(self):
        user = User.objects.create_user(username='dashuser', password='pass12345', role=User.Role.ADMIN)
        self.client.login(username='dashuser', password='pass12345')
        response = self.client.get(reverse('dashboard'))
        self.assertEqual(response.status_code, 200)
        self.assertIn('status_chart_labels', response.context)

    def test_admin_dashboard_sees_full_stats_and_user_count(self):
        admin = User.objects.create_user(username='dashadmin', password='pass12345', role=User.Role.ADMIN)
        other_staff = User.objects.create_user(username='otherstaff', password='pass12345', role=User.Role.STAFF)
        Order.objects.create(customer_name='Someone Else', created_by=other_staff)

        self.client.login(username='dashadmin', password='pass12345')
        response = self.client.get(reverse('dashboard'))
        self.assertTrue(response.context['is_admin'])
        self.assertIn('user_count', response.context)
        # Admin sees every order, including ones they didn't create.
        self.assertEqual(response.context['order_count'], 1)

    def test_staff_dashboard_only_sees_own_orders(self):
        staff = User.objects.create_user(username='dashstaff', password='pass12345', role=User.Role.STAFF)
        other_staff = User.objects.create_user(username='otherstaff2', password='pass12345', role=User.Role.STAFF)
        Order.objects.create(customer_name='Mine', created_by=staff)
        Order.objects.create(customer_name='Not mine', created_by=other_staff)

        self.client.login(username='dashstaff', password='pass12345')
        response = self.client.get(reverse('dashboard'))
        self.assertTrue(response.context['is_staff_role'])
        self.assertNotIn('user_count', response.context)
        # Staff should only see the order they created, not the other staffer's.
        self.assertEqual(response.context['order_count'], 1)
        customer_names = [o.customer_name for o in response.context['latest_orders']]
        self.assertEqual(customer_names, ['Mine'])

    def test_manager_dashboard_sees_all_orders_but_no_user_count(self):
        manager = User.objects.create_user(username='dashmgr', password='pass12345', role=User.Role.MANAGER)
        staff = User.objects.create_user(username='dashstaff2', password='pass12345', role=User.Role.STAFF)
        Order.objects.create(customer_name='Staff order', created_by=staff)

        self.client.login(username='dashmgr', password='pass12345')
        response = self.client.get(reverse('dashboard'))
        self.assertTrue(response.context['is_manager'])
        self.assertNotIn('user_count', response.context)
        self.assertEqual(response.context['order_count'], 1)


class APITests(TestCase):
    def setUp(self):
        self.user = User.objects.create_user(username='apiuser', password='pass12345', role=User.Role.MANAGER)
        self.client.login(username='apiuser', password='pass12345')

    def test_product_list_api_requires_auth(self):
        self.client.logout()
        response = self.client.get('/api/products/')
        self.assertEqual(response.status_code, 403)

    def test_product_list_api_authenticated(self):
        Product.objects.create(name='API Product', length=1, width=1, height=1, weight=1)
        response = self.client.get('/api/products/')
        self.assertEqual(response.status_code, 200)

    def test_order_create_via_api_triggers_recommendation(self):
        product = Product.objects.create(name='API Item', length=5, width=5, height=5, weight=1)
        box = Box.objects.create(name='API Box', length=10, width=10, height=10, max_weight=5, cost=5)
        response = self.client.post('/api/orders/', {
            'customer_name': 'API Customer',
            'products': [product.pk],
        })
        self.assertEqual(response.status_code, 201)
        order = Order.objects.get(customer_name='API Customer')
        self.assertEqual(order.recommended_box, box)
