from django.contrib import admin
from django.contrib.flatpages.admin import FlatPageAdmin
from django.contrib.flatpages.models import FlatPage
from django.contrib.sites.admin import SiteAdmin
from django.contrib.sites.models import Site

from apps.core.models import ProxyFlatPage, ProxySite

# Register your models here.
admin.site.unregister(FlatPage)
admin.site.register(ProxyFlatPage, FlatPageAdmin)


admin.site.unregister(Site)
admin.site.register(ProxySite, SiteAdmin)
