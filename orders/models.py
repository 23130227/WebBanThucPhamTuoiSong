from django.db import models

# Create your models here.
from django.conf import settings
from django.core.validators import MinValueValidator
from django.db import models
from django.db.models import Sum


class Order(models.Model):
    PAYMENT_METHOD_CHOICES = [
        ('cod', 'Thanh toán khi nhận hàng'),
        ('bank', 'Chuyển khoản ngân hàng'),
        ('momo', 'Ví MoMo'),
    ]
    user = models.ForeignKey(
        settings.AUTH_USER_MODEL,
        related_name='orders',
        on_delete=models.SET_NULL,
        null=True,
        blank=True
    )
    full_name = models.CharField(max_length=255)
    phone = models.CharField(max_length=20)
    city = models.CharField(max_length=64)
    district = models.CharField(max_length=64)
    ward = models.CharField(max_length=64)
    address = models.CharField(max_length=255)
    note = models.TextField(blank=True)
    status = models.CharField(
        max_length=32,
        choices=[
            ('pending', 'Chờ xác nhận'),
            ('processing', 'Đang xử lý'),
            ('shipping', 'Đang giao'),
            ('completed', 'Hoàn thành'),
            ('canceled', 'Đã huỷ'),
        ],
        default='pending'
    )
    payment_method = models.CharField(
        max_length=20,
        choices=PAYMENT_METHOD_CHOICES,
        default='cod'
    )
    subtotal = models.PositiveIntegerField(default=0)
    delivery = models.PositiveIntegerField(default=0)
    discount = models.PositiveIntegerField(default=0)
    total = models.PositiveIntegerField(default=0)
    created_at = models.DateTimeField(auto_now_add=True)

    def __str__(self):
        return f"Order #{self.id} | {self.full_name} | {self.total}đ"

    def calculate_subtotal(self):
        return self.items.aggregate(
            total=Sum('total')
        )['total'] or 0

    def calculate_total(self):
        self.subtotal = self.calculate_subtotal()
        self.total = self.subtotal + self.delivery - self.discount
        self.save(update_fields=['subtotal', 'total'])


class OrderItem(models.Model):
    order = models.ForeignKey('Order', related_name='items', on_delete=models.CASCADE)
    product = models.ForeignKey('products.Product', related_name='order_items', on_delete=models.PROTECT)
    batch = models.ForeignKey('products.ProductBatch', related_name='order_items', on_delete=models.SET_NULL, null=True,
                              blank=True)
    product_name = models.CharField(max_length=200)
    product_price = models.PositiveIntegerField()
    quantity = models.PositiveIntegerField(validators=[MinValueValidator(1)])
    total = models.PositiveIntegerField(default=0)

    def __str__(self):
        return f"Order #{self.order_id} | {self.product_name} × {self.quantity}"

    def save(self, *args, **kwargs):
        self.total = self.product_price * self.quantity
        super().save(*args, **kwargs)
