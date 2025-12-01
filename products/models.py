from django.core.exceptions import ValidationError
from django.core.validators import MinValueValidator, MaxValueValidator
from django.db import models
from django.urls import reverse
from django.utils import timezone


# Create your models here.
class Category(models.Model):
    id = models.AutoField(primary_key=True)
    name = models.CharField(max_length=100)
    slug = models.SlugField(max_length=100, unique=True)

    def __str__(self):
        return self.name

    def get_absolute_url(self):
        # Chuyển tới view chi tiết danh mục theo slug
        return reverse("shop-by-category", args=[self.slug])


class Product(models.Model):
    id = models.AutoField(primary_key=True)
    name = models.CharField(max_length=200)
    slug = models.SlugField(max_length=200, unique=True)
    category = models.ForeignKey(Category, related_name='products', on_delete=models.CASCADE)
    description = models.TextField()
    base_price = models.IntegerField()
    quantity = models.IntegerField()
    unit = models.CharField(max_length=50)
    created_at = models.DateTimeField(auto_now_add=True)
    image = models.ImageField(upload_to='products/', blank=True)
    expiry_date = models.DateField()

    def __str__(self):
        return self.name

    def get_absolute_url(self):
        # Chuyển tới view chi tiết sản phẩm theo slug
        return reverse("product-single", args=[self.category.slug, self.slug])

    def get_active_category_promotion(self):
        return CategoryPromotion.objects.filter(category=self.category,
                                                start_date__lte=timezone.now(),
                                                end_date__gte=timezone.now())

    def get_active_product_promotion(self):
        return ProductPromotion.objects.filter(product=self,
                                               start_date__lte=timezone.now(),
                                               end_date__gte=timezone.now())

    def get_discount_percentage(self):
        category_promo = self.get_active_category_promotion()
        product_promo = self.get_active_product_promotion()

        if product_promo.exists():
            return product_promo.first().discount_percentage
        elif category_promo.exists():
            return category_promo.first().discount_percentage
        return 0

    def get_promotional_price(self):
        price = self.base_price
        discount_percentage = self.get_discount_percentage()
        if discount_percentage > 0:
            price = int(round(price * (1 - discount_percentage / 100)))
        return price


class CategoryPromotion(models.Model):
    id = models.AutoField(primary_key=True)
    category = models.ForeignKey(Category, related_name='promotions', on_delete=models.CASCADE)
    discount_percentage = models.DecimalField(max_digits=5, decimal_places=0,
                                              validators=[MinValueValidator(0.0), MaxValueValidator(100.0)])
    start_date = models.DateTimeField()
    end_date = models.DateTimeField()

    def __str__(self):
        return f"{self.category.name} Promotion - {self.discount_percentage}%"

    def clean(self):
        super().clean()
        # 1) Kiểm tra biên hợp lệ
        if self.end_date <= self.start_date:
            raise ValidationError("end_date phải lớn hơn start_date.")

        # 2) Chặn chồng lấp trong cùng category
        qs = CategoryPromotion.objects.filter(category=self.category)
        if self.pk:
            qs = qs.exclude(pk=self.pk)

        # Điều kiện overlap (bao gồm đụng biên):
        # tồn tại promo có start <= new_end và end >= new_start
        if qs.filter(start_date__lte=self.end_date,
                     end_date__gte=self.start_date).exists():
            raise ValidationError("Khoảng thời gian khuyến mãi của danh mục bị chồng lấp.")


class ProductPromotion(models.Model):
    id = models.AutoField(primary_key=True)
    product = models.ForeignKey(Product, related_name='promotions', on_delete=models.CASCADE)
    discount_percentage = models.DecimalField(max_digits=5, decimal_places=0,
                                              validators=[MinValueValidator(0.0), MaxValueValidator(100.0)])
    start_date = models.DateTimeField()
    end_date = models.DateTimeField()

    def __str__(self):
        return f"{self.product.name} Promotion - {self.discount_percentage}%"

    def clean(self):
        super().clean()
        # 1) Kiểm tra biên hợp lệ
        if self.end_date <= self.start_date:
            raise ValidationError("end_date phải lớn hơn start_date.")

        # 2) Chặn chồng lấp trong cùng category
        qs = ProductPromotion.objects.filter(product=self.product)
        if self.pk:
            qs = qs.exclude(pk=self.pk)

        # Điều kiện overlap (bao gồm đụng biên):
        # tồn tại promo có start <= new_end và end >= new_start
        if qs.filter(start_date__lte=self.end_date,
                     end_date__gte=self.start_date).exists():
            raise ValidationError("Khoảng thời gian khuyến mãi của danh mục bị chồng lấp.")


class Review(models.Model):
    id = models.AutoField(primary_key=True)
    product = models.ForeignKey(Product, related_name='reviews', on_delete=models.CASCADE)
    user_name = models.CharField(max_length=100)
    rating = models.IntegerField()
    comment = models.TextField()
    created_at = models.DateTimeField(auto_now_add=True)

    def __str__(self):
        return f"Review for {self.product.name} by {self.user_name}"
