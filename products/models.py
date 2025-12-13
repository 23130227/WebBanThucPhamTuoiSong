from django.contrib.auth.models import User
from django.core.exceptions import ValidationError
from django.core.validators import MinValueValidator, MaxValueValidator
from django.db import models
from django.urls import reverse
from django.utils import timezone


# Create your models here.
class ProductQuerySet(models.QuerySet):
    def active(self):
        return self.filter(is_active=True, expiry_date__gte=timezone.now().date())


class Product(models.Model):
    id = models.AutoField(primary_key=True)
    name = models.CharField(max_length=200)
    slug = models.SlugField(max_length=200, unique=True, allow_unicode=True)
    category = models.ForeignKey('Category', related_name='products', on_delete=models.CASCADE)
    description = models.TextField()
    unit = models.CharField(max_length=50)
    quantity = models.IntegerField(validators=[MinValueValidator(0)])
    sold_quantity = models.IntegerField(default=0, validators=[MinValueValidator(0)])
    base_price = models.IntegerField(validators=[MinValueValidator(0)])
    expiry_date = models.DateField()
    image = models.ImageField(upload_to='products/', blank=True)
    created_at = models.DateTimeField(auto_now_add=True)
    is_active = models.BooleanField(default=True)
    objects = ProductQuerySet.as_manager()

    def __str__(self):
        return self.name

    def get_absolute_url(self):
        return reverse("product-single", args=[self.category.slug, self.slug])

    def get_active_product_discount(self):
        return ProductDiscount.objects.filter(product=self,
                                              start_date__lte=timezone.now(),
                                              end_date__gte=timezone.now())

    def get_active_category_discount(self):
        return CategoryDiscount.objects.filter(category=self.category,
                                               start_date__lte=timezone.now(),
                                               end_date__gte=timezone.now())

    def get_discount_percentage(self):
        product_discount = self.get_active_product_discount()
        category_discount = self.get_active_category_discount()

        if product_discount.exists():
            return product_discount.first().discount_percentage
        elif category_discount.exists():
            return category_discount.first().discount_percentage
        return 0

    def get_discount_price(self):
        price = self.base_price
        discount_percentage = self.get_discount_percentage()
        if discount_percentage > 0:
            price = int(round(price * (1 - discount_percentage / 100)))
        return price


class Category(models.Model):
    id = models.AutoField(primary_key=True)
    name = models.CharField(max_length=100)
    slug = models.SlugField(max_length=200, unique=True, allow_unicode=True)

    def __str__(self):
        return self.name

    def get_absolute_url(self):
        return reverse("shop-by-category", args=[self.slug])


class ProductDiscount(models.Model):
    id = models.AutoField(primary_key=True)
    product = models.ForeignKey('Product', related_name='discounts', on_delete=models.CASCADE)
    discount_percentage = models.DecimalField(max_digits=5, decimal_places=0,
                                              validators=[MinValueValidator(0.0), MaxValueValidator(100.0)])
    start_date = models.DateTimeField()
    end_date = models.DateTimeField()

    def __str__(self):
        return f"{self.product.name} Promotion - {self.discount_percentage}%"

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
    id = models.AutoField(primary_key=True)
    category = models.ForeignKey('Category', related_name='discounts', on_delete=models.CASCADE)
    discount_percentage = models.DecimalField(max_digits=5, decimal_places=0,
                                              validators=[MinValueValidator(0.0), MaxValueValidator(100.0)])
    start_date = models.DateTimeField()
    end_date = models.DateTimeField()

    def __str__(self):
        return f"{self.category.name} Discount - {self.discount_percentage}%"

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


class Review(models.Model):
    id = models.AutoField(primary_key=True)
    product = models.ForeignKey('Product', related_name='reviews', on_delete=models.CASCADE)
    rating = models.IntegerField(validators=[MinValueValidator(1), MaxValueValidator(5)])
    user = models.ForeignKey(User, related_name='reviews', on_delete=models.CASCADE)
    comment = models.TextField()
    created_at = models.DateTimeField(auto_now_add=True)

    def __str__(self):
        return f"Review for {self.product.name} by {self.user.username}"
