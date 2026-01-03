from django.contrib import admin

# Register your models here.
from django.contrib import admin
from .models import Profile


@admin.register(Profile)
class ProfileAdmin(admin.ModelAdmin):
    list_display = (
        'user',
        'phone',
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