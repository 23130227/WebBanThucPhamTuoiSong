from django.contrib import admin

from .models import *


# Register your models here.
@admin.register(Product)
class ProductAdmin(admin.ModelAdmin):
    list_display = (
        'name',
        'category',
        'base_price',
        'available_quantity',
        'sold_quantity',
        'is_active',
        'created_at',
    )
    list_editable = ('is_active',)
    readonly_fields = (
        'slug',
        'sold_quantity',
        'created_at',
    )
    list_filter = ('category', 'is_active')
    search_fields = ('name',)

    def available_quantity(self, obj):
        return obj.get_available_quantity()


@admin.register(ProductBatch)
class ProductBatchAdmin(admin.ModelAdmin):
    list_display = (
        'product',
        'expiry_date',
        'stock_quantity',
        'remaining_quantity',
    )
    readonly_fields = (
        'remaining_quantity',
        'created_at',
    )
    list_filter = ('product', 'expiry_date',)
    ordering = ('expiry_date',)


@admin.register(Category)
class CategoryAdmin(admin.ModelAdmin):
    list_display = ('name',)
    readonly_fields = ('slug',)
    search_fields = ('name',)


@admin.register(ProductDiscount)
class ProductDiscountAdmin(admin.ModelAdmin):
    list_display = (
        'product',
        'discount_percentage',
        'start_date',
        'end_date',
    )
    list_filter = ('product', 'start_date', 'end_date',)


@admin.register(CategoryDiscount)
class CategoryDiscountAdmin(admin.ModelAdmin):
    list_display = (
        'category',
        'discount_percentage',
        'start_date',
        'end_date',
    )
    list_filter = ('category', 'start_date', 'end_date',)


@admin.register(ExpiryDiscount)
class ExpiryDiscountAdmin(admin.ModelAdmin):
    list_display = (
        'category',
        'days_before_expiry',
        'discount_percentage',
    )
    list_filter = ('category',)


@admin.register(Review)
class ReviewAdmin(admin.ModelAdmin):
    list_display = (
        'product',
        'user',
        'rating',
        'sentiment_badge',
        'positive_percent',
        'created_at',
    )

    readonly_fields = (
        'product',
        'user',
        'rating',
        'comment',
        'created_at',
        'ai_positive_score',
        'ai_negative_score',
        'ai_sentiment',
    )

    list_filter = (
        'rating',
        'ai_sentiment',
        'created_at',
    )

    search_fields = (
        'product__name',
        'user__username',
        'comment',
    )

    # ---- HIỂN THỊ % ----
    def positive_percent(self, obj):
        if obj.ai_positive_score is None:
            return "-"
        return f"{obj.ai_positive_score * 100:.1f}%"

    positive_percent.short_description = "AI Positive"

    # ---- HIỂN THỊ BADGE MÀU ----
    def sentiment_badge(self, obj):
        if obj.ai_sentiment == "positive":
            return "🟢 Positive"
        elif obj.ai_sentiment == "negative":
            return "🔴 Negative"
        return "⚪ N/A"

    sentiment_badge.short_description = "Sentiment"


@admin.register(WishlistItem)
class WishlistItemAdmin(admin.ModelAdmin):
    list_display = (
        'user',
        'product',
        'created_at',
    )

    readonly_fields = (
        'user',
        'product',
        'created_at',
    )

    list_filter = (
        'created_at',
    )

    search_fields = (
        'user__username',
        'product__name',
    )

    ordering = ('-created_at',)
