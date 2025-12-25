from django.contrib.auth import get_user_model
from django.test import TestCase
from django.urls import reverse

from .models import Order, OrderItem
from products.models import Category, Product


class OrderViewsTests(TestCase):
    def setUp(self):
        User = get_user_model()
        self.user_a = User.objects.create_user(username='a', password='pass12345')
        self.user_b = User.objects.create_user(username='b', password='pass12345')

        self.category = Category.objects.create(name='Rau', slug='rau')
        self.product = Product.objects.create(
            name='Test Product',
            slug='test-product',
            category=self.category,
            description='desc',
            unit='kg',
            unit_size=1,
            stock_quantity=10,
            sold_quantity=0,
            base_price=100,
            expiry_date='2099-01-01T00:00:00Z',
            is_active=True,
        )

        self.order_a = Order.objects.create(
            user=self.user_a,
            full_name='A',
            phone='000',
            city='c',
            district='d',
            ward='w',
            address='addr',
            note='',
            status='pending',
            payment_method='cod',
            subtotal=100,
            delivery=0,
            discount=0,
            total=100,
        )
        OrderItem.objects.create(
            order=self.order_a,
            product=self.product,
            product_name=self.product.name,
            product_price=100,
            quantity=1,
            total=100,
        )

        self.order_b = Order.objects.create(
            user=self.user_b,
            full_name='B',
            phone='111',
            city='c',
            district='d',
            ward='w',
            address='addr',
            note='',
            status='pending',
            payment_method='cod',
            subtotal=100,
            delivery=0,
            discount=0,
            total=100,
        )

    def test_order_history_requires_login(self):
        resp = self.client.get(reverse('order_history'))
        self.assertEqual(resp.status_code, 302)

    def test_order_history_lists_only_current_user_orders(self):
        self.client.login(username='a', password='pass12345')
        resp = self.client.get(reverse('order_history'))
        self.assertEqual(resp.status_code, 200)
        self.assertContains(resp, f"#{self.order_a.id}")
        self.assertNotContains(resp, f"#{self.order_b.id}")

    def test_order_single_requires_login(self):
        url = reverse('order_single', args=[self.order_a.id])
        self.assertEqual(url, f"/order/order-single{self.order_a.id}/")
        resp = self.client.get(url)
        self.assertEqual(resp.status_code, 302)

    def test_order_single_enforces_ownership(self):
        self.client.login(username='b', password='pass12345')
        url = reverse('order_single', args=[self.order_a.id])
        self.assertEqual(url, f"/order/order-single{self.order_a.id}/")
        resp = self.client.get(url)
        self.assertEqual(resp.status_code, 404)

    def test_order_history_pagination(self):
        # create enough orders for pagination (page size is 10)
        bulk = [
            Order(
                user=self.user_a,
                full_name='A',
                phone='000',
                city='c',
                district='d',
                ward='w',
                address='addr',
                note='',
                status='pending',
                payment_method='cod',
                subtotal=1,
                delivery=0,
                discount=0,
                total=1,
            )
            for _ in range(15)
        ]
        Order.objects.bulk_create(bulk)

        self.client.login(username='a', password='pass12345')
        resp1 = self.client.get(reverse('order_history'))
        self.assertEqual(resp1.status_code, 200)
        self.assertTrue(resp1.context['page_obj'].paginator.num_pages >= 2)

        resp2 = self.client.get(reverse('order_history') + '?page=2')
        self.assertEqual(resp2.status_code, 200)
