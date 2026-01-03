from django.contrib import admin

from pages.models import HomeSlide


# Register your models here.
@admin.register(HomeSlide)
class HomeSliderAdmin(admin.ModelAdmin):
    list_display = (
        'title',
        'order',
        'is_active',
        'created_at',
    )
    list_editable = (
        'order',
        'is_active',
    )
    readonly_fields = (
        'created_at',
    )
    list_filter = (
        'is_active',
    )
    search_fields = (
        'title',
        'subtitle',
    )
