from django.contrib import admin
from .models import *


# Register your models here.
class OrderItemInline(admin.TabularInline):
    model = OrderItem
    extra = 0
    can_delete = False

    readonly_fields = (
        'product_name',
        'batch',
        'quantity',
        'product_price',
        'total',
    )


@admin.register(Order)
class OrderAdmin(admin.ModelAdmin):
    list_display = (
        'id',
        'full_name',
        'status',
        'payment_method',
        'total',
        'created_at',
    )
    readonly_fields = (
        'subtotal',
        'total',
        'created_at',
    )
    list_filter = ('status', 'payment_method',)
    search_fields = ('full_name', 'phone',)
    list_editable = ('status',)
    inlines = [OrderItemInline]


@admin.register(OrderItem)
class OrderItemAdmin(admin.ModelAdmin):
    list_display = (
        'order',
        'product_name',
        'quantity',
        'product_price',
        'total',
    )
    readonly_fields = (
        'order',
        'product',
        'batch',
        'product_name',
        'product_price',
        'quantity',
        'total',
    )
