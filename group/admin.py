from django.contrib import admin

from group.models import User


class UserAdmin(admin.ModelAdmin):
    list_display = ('user_id', 'last_update')
    list_display_links = ('user_id', 'last_update')
    ordering = ('user_id',)


admin.site.register(User, UserAdmin)
