from django.contrib import admin
from django.utils.html import format_html

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
        'get_positive_percentage',  # Thêm cột positive %
        'is_active',
        'created_at',
    )
    list_editable = ('is_active',)
    readonly_fields = (
        'slug',
        'sold_quantity',
        'created_at',
        'get_review_stats',  # Thêm thống kê vào trang detail
    )
    list_filter = ('category', 'is_active')
    search_fields = ('name',)

    def available_quantity(self, obj):
        return obj.get_available_quantity()

    @admin.display(description='Positive %')
    def get_positive_percentage(self, obj):
        """Hiển thị phần trăm positive trong danh sách"""
        percentage = obj.positive_percentage
        if percentage is None:
            return format_html('<span style="color: gray;">—</span>')

        if percentage >= 70:
            color = '#28a745'  # Xanh lá
            emoji = '🟢'
        elif percentage >= 40:
            color = '#ffc107'  # Vàng cam
            emoji = '🟡'
        else:
            color = '#dc3545'  # Đỏ
            emoji = '🔴'

        # Format số trước khi truyền vào format_html
        percentage_str = f"{percentage:.1f}%"

        return format_html(
            '{} <span style="color: {}; font-weight: bold;">{}</span>',
            emoji,
            color,
            percentage_str
        )

    @admin.display(description='Thống kê đánh giá')
    def get_review_stats(self, obj):
        """Hiển thị thống kê chi tiết trong trang detail"""
        stats = obj.review_stats

        if stats['total'] == 0:
            return format_html(
                '<span style="color: gray; font-style: italic;">Chưa có đánh giá nào</span>'
            )

        # Format số trước
        positive_pct = f"{stats['positive_percentage'] or 0:.1f}%"
        negative_pct = f"{stats['negative_percentage'] or 0:.1f}%"

        return format_html(
            '''
            <div style="line-height: 1.8; padding: 10px; background: none; border-radius: 5px;">
                <div><strong>Tổng đánh giá:</strong> {}</div>
                <div><strong>🟢 Positive:</strong> {} ({})</div>
                <div><strong>🔴 Negative:</strong> {} ({})</div>
            </div>
            ''',
            stats['total'],
            stats['positive'],
            positive_pct,
            stats['negative'],
            negative_pct,
        )


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