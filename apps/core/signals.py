from django.apps import apps
from django.contrib.sites.models import Site
from django.db.models.signals import post_migrate
from django.dispatch import receiver

from .models import Site


@receiver(post_migrate, sender=apps.get_app_config('core'))
def create_localhost_site(sender, **kwargs):
    localhost = '127.0.0.1'
    if not Site.objects.filter(domain=localhost).exists():
        Site.objects.create(domain=localhost, name='localhost')
