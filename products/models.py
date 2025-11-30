from django.db import models
from django.urls import reverse


# Create your models here.
class Category(models.Model):
    id = models.AutoField(primary_key=True)
    name = models.CharField(max_length=100)
    slug = models.SlugField(max_length=100, unique=True)

    def __str__(self):
        return self.name


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


class CategoryPromotion(models.Model):
    id = models.AutoField(primary_key=True)
    category = models.ForeignKey(Category, related_name='promotions', on_delete=models.CASCADE)
    discount_percentage = models.FloatField()
    start_date = models.DateTimeField()
    end_date = models.DateTimeField()

    def __str__(self):
        return f"{self.category.name} Promotion - {self.discount_percentage}%"


class ProductPromotion(models.Model):
    id = models.AutoField(primary_key=True)
    product = models.ForeignKey(Product, related_name='promotions', on_delete=models.CASCADE)
    discount_percentage = models.FloatField()
    start_date = models.DateTimeField()
    end_date = models.DateTimeField()

    def __str__(self):
        return f"{self.product.name} Promotion - {self.discount_percentage}%"


class Review(models.Model):
    id = models.AutoField(primary_key=True)
    product = models.ForeignKey(Product, related_name='reviews', on_delete=models.CASCADE)
    user_name = models.CharField(max_length=100)
    rating = models.IntegerField()
    comment = models.TextField()
    created_at = models.DateTimeField(auto_now_add=True)

    def __str__(self):
        return f"Review for {self.product.name} by {self.user_name}"
