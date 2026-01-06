from django.contrib.auth.models import User
from django.core.exceptions import ValidationError
from django.core.validators import MinValueValidator, MaxValueValidator
from django.db import models
from django.db.models import Sum
from django.urls import reverse
from django.utils import timezone
from django.utils.text import slugify

from orders.models import OrderItem


# Create your models here.
class ProductQuerySet(models.QuerySet):
    def active(self):
        valid_batches = ProductBatch.objects.filter(
            product=models.OuterRef('pk'),
            expiry_date__gt=timezone.now(),
            remaining_quantity__gt=0
        )
        return self.filter(is_active=True).annotate(
            has_valid_batch=models.Exists(valid_batches)
        ).filter(has_valid_batch=True)


class Product(models.Model):
    UNIT_CHOICES = [
        ('g', 'Gram (g)'),
        ('kg', 'Kilogram (kg)'),
        ('pcs', 'Cái / Miếng'),
        ('bunch', 'Bó'),
        ('bag', 'Túi'),
        ('ml', 'Milliliter (ml)'),
        ('l', 'Lít (l)'),
        ('bottle', 'Chai'),
        ('pack', 'Gói / Hộp'),
    ]
    name = models.CharField(max_length=200)
    slug = models.SlugField(unique=True, allow_unicode=True)
    category = models.ForeignKey('Category', related_name='products', on_delete=models.CASCADE)
    description = models.TextField()
    unit = models.CharField(max_length=50, choices=UNIT_CHOICES)
    unit_size = models.PositiveIntegerField(default=500)
    sold_quantity = models.PositiveIntegerField(default=0)
    base_price = models.PositiveIntegerField()
    image = models.ImageField(upload_to='products/', blank=True, null=True)
    created_at = models.DateTimeField(auto_now_add=True)
    is_active = models.BooleanField(default=True)
    objects = ProductQuerySet.as_manager()

    def save(self, *args, **kwargs):
        if not self.slug:
            base_slug = slugify(self.name)
            slug = base_slug
            counter = 1
            while Product.objects.filter(slug=slug).exclude(pk=self.pk).exists():
                slug = f"{base_slug}-{counter}"
                counter += 1
            self.slug = slug
        super().save(*args, **kwargs)

    def clean(self):
        super().clean()
        if Product.objects.exclude(pk=self.pk).filter(name__iexact=self.name).exists():
            raise ValidationError("Tên sản phẩm đã tồn tại.")

    def __str__(self):
        return f"{self.name} ({self.category.name})"

    def get_absolute_url(self):
        return reverse("product_single", args=[self.category.slug, self.slug])

    def get_available_quantity(self):
        result = self.batches.filter(
            remaining_quantity__gt=0,
            expiry_date__gt=timezone.now()
        ).aggregate(
            total=Sum('remaining_quantity')
        )
        return result['total'] or 0

    def get_discount_percentage_preview(self):
        batch = self.batches.filter(remaining_quantity__gt=0, expiry_date__gt=timezone.now()).order_by(
            'expiry_date').first()
        if batch:
            return batch.get_discount_percentage()
        return 0

    def get_discount_price_preview(self):
        batch = self.batches.filter(remaining_quantity__gt=0, expiry_date__gt=timezone.now()).order_by(
            'expiry_date').first()
        if batch:
            return batch.get_discount_price()
        return self.base_price

    def allocate_order_items(self, order, quantity):
        items = []
        for batch in self.batches.filter(
                remaining_quantity__gt=0, expiry_date__gt=timezone.now()
        ).order_by('expiry_date'):
            if quantity <= 0:
                break
            take_qty = min(batch.remaining_quantity, quantity)
            item = OrderItem(
                order=order,
                product=self,
                batch=batch,
                product_name=self.name,
                product_price=batch.get_discount_price(),
                quantity=take_qty
            )
            items.append(item)
            quantity -= take_qty

        if quantity > 0:
            raise ValidationError(f"Không đủ tồn kho cho {self.name}.")
        return items


class ProductBatch(models.Model):
    product = models.ForeignKey('Product', related_name='batches', on_delete=models.CASCADE)
    stock_quantity = models.PositiveIntegerField()
    remaining_quantity = models.PositiveIntegerField()
    expiry_date = models.DateTimeField()
    created_at = models.DateTimeField(auto_now_add=True)

    class Meta:
        ordering = ['expiry_date']

    def save(self, *args, **kwargs):
        if not self.pk:
            self.remaining_quantity = self.stock_quantity
        else:
            old = ProductBatch.objects.filter(pk=self.pk).only('stock_quantity', 'remaining_quantity').first()
            if old.stock_quantity != self.stock_quantity:
                difference = self.stock_quantity - old.stock_quantity
                self.remaining_quantity += difference
                if self.remaining_quantity < 0:
                    self.remaining_quantity = 0
        super().save(*args, **kwargs)

    def clean(self):
        super().clean()
        if self.expiry_date <= timezone.now():
            raise ValidationError("expiry_date phải là một ngày trong tương lai.")

    def __str__(self):
        return (
            f"{self.product.name} | "
            f"EXP: {self.expiry_date.date()} | "
            f"Remaining: {self.remaining_quantity}"
        )

    def days_to_expiry(self):
        delta = self.expiry_date - timezone.now()
        return max(0, int(delta.total_seconds() / 86400))

    def get_discount_percentage(self):
        product_discount = ProductDiscount.objects.filter(product=self.product,
                                                          start_date__lte=timezone.now(),
                                                          end_date__gte=timezone.now()).first()
        category_discount = CategoryDiscount.objects.filter(category=self.product.category,
                                                            start_date__lte=timezone.now(),
                                                            end_date__gte=timezone.now()).first()

        if product_discount:
            base_discount = product_discount.discount_percentage
        elif category_discount:
            base_discount = category_discount.discount_percentage
        else:
            base_discount = 0

        # lấy expiry discount
        expiry_discount = ExpiryDiscount.objects.filter(
            category=self.product.category,
            days_before_expiry__gte=self.days_to_expiry()
        ).order_by('-days_before_expiry').first()
        expiry_discount_pct = expiry_discount.discount_percentage if expiry_discount else 0

        # so sánh với expiry discount
        return max(base_discount, expiry_discount_pct)

    def get_discount_price(self):
        discount_percentage = self.get_discount_percentage()
        return int(round(self.product.base_price * (1 - discount_percentage / 100)))


class Category(models.Model):
    name = models.CharField(max_length=100)
    slug = models.SlugField(unique=True, allow_unicode=True)

    def save(self, *args, **kwargs):
        if not self.slug:
            base_slug = slugify(self.name)
            slug = base_slug
            counter = 1
            while Category.objects.filter(slug=slug).exclude(pk=self.pk).exists():
                slug = f"{base_slug}-{counter}"
                counter += 1
            self.slug = slug
        super().save(*args, **kwargs)

    def clean(self):
        super().clean()
        if Category.objects.exclude(pk=self.pk).filter(name__iexact=self.name).exists():
            raise ValidationError("Tên danh mục đã tồn tại.")

    def __str__(self):
        return self.name

    def get_absolute_url(self):
        return reverse("shop_by_category", args=[self.slug])


class ProductDiscount(models.Model):
    product = models.ForeignKey('Product', related_name='discounts', on_delete=models.CASCADE)
    discount_percentage = models.PositiveSmallIntegerField(validators=[MaxValueValidator(100)])
    start_date = models.DateTimeField()
    end_date = models.DateTimeField()

    def __str__(self):
        return (
            f"{self.product.name} - {self.discount_percentage}% "
            f"({self.start_date.date()} → {self.end_date.date()})"
        )

    def clean(self):
        super().clean()
        if self.end_date <= self.start_date:
            raise ValidationError("end_date phải lớn hơn start_date.")

        qs = ProductDiscount.objects.filter(product=self.product)
        if self.pk:
            qs = qs.exclude(pk=self.pk)

        if qs.filter(start_date__lte=self.end_date,
                     end_date__gte=self.start_date).exists():
            raise ValidationError("Khoảng thời gian khuyến mãi của danh mục bị chồng lấp.")


class CategoryDiscount(models.Model):
    category = models.ForeignKey('Category', related_name='discounts', on_delete=models.CASCADE)
    discount_percentage = models.PositiveSmallIntegerField(validators=[MaxValueValidator(100)])
    start_date = models.DateTimeField()
    end_date = models.DateTimeField()

    def __str__(self):
        return (
            f"{self.category.name} - {self.discount_percentage}% "
            f"({self.start_date.date()} → {self.end_date.date()})"
        )

    def clean(self):
        super().clean()
        if self.end_date <= self.start_date:
            raise ValidationError("end_date phải lớn hơn start_date.")

        qs = CategoryDiscount.objects.filter(category=self.category)
        if self.pk:
            qs = qs.exclude(pk=self.pk)

        if qs.filter(start_date__lte=self.end_date,
                     end_date__gte=self.start_date).exists():
            raise ValidationError("Khoảng thời gian khuyến mãi của danh mục bị chồng lấp.")


class ExpiryDiscount(models.Model):
    category = models.ForeignKey('Category', related_name='expiry_discounts', on_delete=models.CASCADE)
    days_before_expiry = models.PositiveIntegerField()
    discount_percentage = models.PositiveSmallIntegerField(validators=[MaxValueValidator(100)])

    class Meta:
        unique_together = ('category', 'days_before_expiry')

    def __str__(self):
        return (
            f"{self.category.name} | "
            f"≤ {self.days_before_expiry} days | "
            f"{self.discount_percentage}%"
        )

    def clean(self):
        super().clean()
        qs = ExpiryDiscount.objects.filter(
            category=self.category,
            days_before_expiry=self.days_before_expiry
        )
        if self.pk:
            qs = qs.exclude(pk=self.pk)

        if qs.exists():
            raise ValidationError("Đã tồn tại khuyến mãi.")


class Review(models.Model):
    product = models.ForeignKey('Product', related_name='reviews', on_delete=models.CASCADE)
    rating = models.PositiveIntegerField(validators=[MinValueValidator(1), MaxValueValidator(5)])
    user = models.ForeignKey(User, related_name='reviews', on_delete=models.CASCADE)
    comment = models.TextField()
    created_at = models.DateTimeField(auto_now_add=True)

    def __str__(self):
        return f"{self.user.username} → {self.product.name} ({self.rating}★)"


class WishlistItem(models.Model):
    user = models.ForeignKey(User, related_name='wishlist_items', on_delete=models.CASCADE)
    product = models.ForeignKey('Product', related_name='wishlisted_by', on_delete=models.CASCADE)
    created_at = models.DateTimeField(auto_now_add=True)

    class Meta:
        unique_together = ('user', 'product')
        ordering = ['-created_at']

    def __str__(self):
        return f"{self.user.username}  {self.product.name}"

