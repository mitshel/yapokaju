from django.db import models
from django.db.models import OuterRef, Subquery
from django.utils import timezone
from django.utils.translation import ugettext_lazy as _

from apps.core.models import TimestampsMixin

# Create your models here.
EVENT_TYPE_EXCURSION = 5
EVENT_TYPE_CHOICES = (
    (EVENT_TYPE_EXCURSION, 'Экскурсия'),
)


class EventManager(models.Manager):
    def get_queryset(self):
        queryset = super(EventManager, self).get_queryset()

        datetime_queryset = EventDatetime.objects \
            .filter(event=OuterRef('pk'), active=True, datetime__gt=timezone.now()) \
            .values('datetime') \
            .order_by('datetime')
        queryset = queryset.annotate(datetime=Subquery(datetime_queryset[:1])) \
            .order_by('datetime', '-id')
        return queryset


class Event(TimestampsMixin):
    name = models.CharField('название', max_length=128, default='')
    description = models.TextField('описание', max_length=2048, default='',
                                   help_text='Не более 2048 знаков.')
    image = models.ImageField(null=True, blank=True)
    type = models.PositiveIntegerField('тип события', choices=EVENT_TYPE_CHOICES,
                                       default=EVENT_TYPE_EXCURSION)
    recursive = models.BooleanField('повторяющиеся', default=False) 
    user = models.ForeignKey('account.User', null=True, related_name='events',
                             on_delete=models.SET_NULL)

    default_manager = models.Manager()
    objects = EventManager()

    class Meta(object):
        verbose_name = _('event')
        verbose_name_plural = _('events')

    def __str__(self):
        return self.name


class EventDatetime(TimestampsMixin):
    datetime = models.DateTimeField(_('date and time'), null=True)
    active = models.BooleanField(default=True)
    event = models.ForeignKey('clndr.Event', related_name='datetime_set',
                              on_delete=models.CASCADE)

    class Meta(object):
        verbose_name = _('datetime')
        verbose_name_plural = _('datetime set')
        ordering = ('datetime', )
