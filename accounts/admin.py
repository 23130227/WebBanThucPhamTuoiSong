from django.contrib import admin

# Register your models here.
from django.contrib import admin
from .models import Profile


@admin.register(Profile)
class ProfileAdmin(admin.ModelAdmin):
    list_display = (
        'user',
        'phone',
        'short_address',
    )
    readonly_fields = (
        'user',
    )
    search_fields = (
        'user__username',
        'user__email',
        'phone',
    )
    list_select_related = ('user',)

    def short_address(self, obj):
        if not obj.address:
            return "-"
        return obj.address[:40] + "..." if len(obj.address) > 40 else obj.address

    short_address.short_description = "Địa chỉ"
