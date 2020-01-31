from django.contrib import admin

from eventlog.models import Log


class LogAdmin(admin.ModelAdmin):
    list_display = ('user', 'date', 'event', 'count')
    list_display_links = ('user', 'date', 'event', 'count')
    ordering = ('date', 'event', 'user')


admin.site.register(Log, LogAdmin)
