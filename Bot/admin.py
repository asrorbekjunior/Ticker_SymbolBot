from django.contrib import admin
from .models import TelegramUser

@admin.register(TelegramUser)
class TelegramUserAdmin(admin.ModelAdmin):
    list_display = ('user_id', 'first_name', 'last_name', 'username', 'status', 'date_joined', 'last_active')
    list_filter = ('status', 'date_joined')
    search_fields = ('user_id', 'first_name', 'last_name', 'username')
    readonly_fields = ('date_joined', 'last_active')

    fieldsets = (
        (None, {
            'fields': ('user_id', 'first_name', 'last_name', 'username', 'status')
        }),
        ('Advanced options', {
            'classes': ('collapse',),
            'fields': ('extra_info', 'date_joined', 'last_active'),
        }),
    )
