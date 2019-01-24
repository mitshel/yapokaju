from django.contrib import admin

from .models import (Event, EventDatetime, EventFeedback, Member, Restriction,
                     Template, TemplateImage)


# Register your models here.
class EventDatetimeInline(admin.TabularInline):
    model = EventDatetime

    extra = 1


class EventAdmin(admin.ModelAdmin):
    list_display = ('recursive', 'user')
    list_filter = ('recursive', )

    inlines = [
        EventDatetimeInline,
    ]

admin.site.register(Event, EventAdmin)


class TemplateImageInline(admin.TabularInline):
    model = TemplateImage
    fields = ('file', 'alt')

    extra = 1


class TemplateAdmin(admin.ModelAdmin):
    list_display = ('name', 'type')
    list_filter = ('type', )

    inlines = [
        TemplateImageInline,
    ]

admin.site.register(Template, TemplateAdmin)


admin.site.register(Member)
admin.site.register(EventFeedback)
admin.site.register(Restriction)
