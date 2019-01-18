from django.contrib import admin

from .models import Event, EventDatetime

# Register your models here.
class EventDatetimeInline(admin.TabularInline):
    model = EventDatetime

    extra = 1


class EventAdmin(admin.ModelAdmin):
    list_display = ('name', 'type', 'recursive', 'user')
    list_filter = ('type', 'recursive')

    inlines = [
        EventDatetimeInline,
    ]
admin.site.register(Event, EventAdmin)
