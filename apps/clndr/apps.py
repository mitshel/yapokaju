from django.apps import AppConfig


class ClndrConfig(AppConfig):
    name = 'apps.clndr'

    verbose_name = 'The calendar'

    def ready(self):
        from . import signals
