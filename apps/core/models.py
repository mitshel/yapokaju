from django.contrib.flatpages.models import FlatPage
from django.contrib.sites.models import Site
from django.db import models
from django.utils.translation import ugettext_lazy as _


# Create your models here.
class TimestampsMixin(models.Model):
    """
    Timestamp поля created_at и updated_at для моделей.
    """

    created_at = models.DateTimeField(_('time of creation'), null=True,
                                      auto_now_add=True)
    updated_at = models.DateTimeField(_('last modification time'), null=True,
                                      auto_now=True)

    class Meta(object):
        abstract = True  


class ProxySite(Site):

    class Meta(object):
        proxy = True

        verbose_name = _('site')
        verbose_name_plural = _('sites')
        ordering = ('domain', )

        default_permissions = ()


class ProxyFlatPage(FlatPage):

    class Meta(object):
        proxy = True

        verbose_name = _('flat page')
        verbose_name_plural = _('flat pages')
        ordering = ('url', )
        default_permissions = ()
