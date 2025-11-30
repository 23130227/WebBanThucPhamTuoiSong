from django.contrib import admin

from .models import *

# Register your models here.
admin.site.register(Category)
admin.site.register(Product)
admin.site.register(CategoryPromotion)
admin.site.register(ProductPromotion)
admin.site.register(Review)
