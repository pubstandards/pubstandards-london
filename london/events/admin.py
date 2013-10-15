from django.contrib import admin
from london.events.models import Event


class EventAdmin(admin.ModelAdmin):
    prepopulated_fields = { 'slug': ( 'title', ) }

admin.site.register(Event, EventAdmin)
