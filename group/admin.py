from django.contrib import admin

from group.models import User, Person


class UserAdmin(admin.ModelAdmin):
    list_display = ('user_id', 'last_update')
    list_display_links = ('user_id', 'last_update')
    ordering = ('user_id',)


admin.site.register(User, UserAdmin)


class PersonAdmin(admin.ModelAdmin):
    list_display = ('person_id', 'name', 'role', 'user')
    list_display_links = ('person_id', 'name')
    ordering = ('user',)


admin.site.register(Person, PersonAdmin)
