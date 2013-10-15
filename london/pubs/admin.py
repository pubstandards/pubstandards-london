from django.contrib import admin
from london.pubs.models import Pub


class PubAdmin(admin.ModelAdmin):
    prepopulated_fields = { 'slug': ( 'name', ) }

admin.site.register(Pub, PubAdmin)
