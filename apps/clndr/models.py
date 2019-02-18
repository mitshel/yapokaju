from django.db import models
from django.db.models import Count, OuterRef, Q, Subquery, Sum
from django.urls import reverse
from django.utils import timezone
from django.utils.translation import ugettext_lazy as _

from apps.core.models import TimestampsMixin

# Create your models here.
EVENT_TYPE_EXCURSION = 5
EVENT_TYPE_CHOICES = (
    (EVENT_TYPE_EXCURSION, 'Экскурсия'),
)


class TemplateManager(models.Manager):
    def get_queryset(self):
        queryset = super(TemplateManager, self).get_queryset()

        queryset = queryset.select_related('image')
        return queryset


class Template(TimestampsMixin):
    name = models.CharField('название', max_length=128, default='')
    short_description = models.TextField('краткое описание', default='')
    description = models.TextField('описание', default='')
    type = models.PositiveIntegerField('тип события', choices=EVENT_TYPE_CHOICES,
                                       default=EVENT_TYPE_EXCURSION)
    image = models.OneToOneField('clndr.TemplateImage', verbose_name='главное изображени',
                                 null=True, blank=True, related_name='+',
                                 on_delete=models.SET_NULL)
    map_addr = models.CharField('Координаты YandexMaps', max_length=256, default='')
    file = models.FileField(upload_to='files/%Y/%m/%d', null=True, blank=True)   
    
    default_manager = models.Manager()
    objects = TemplateManager()

    class Meta(object):
        verbose_name = _('template')
        verbose_name_plural = _('templates')

    def __str__(self):
        return self.name


class TemplateImage(TimestampsMixin):
    alt = models.CharField('alternate text', max_length=128, default='', blank=True)
    file = models.ImageField(upload_to='images/%Y/%m/%d')
    template = models.ForeignKey('clndr.Template', null=True, related_name='images',
                                 on_delete=models.SET_NULL)

    class Meta(object):
        verbose_name = _('image')
        verbose_name_plural = _('images')

    def __str__(self):
        return self.file.name


class EventManager(models.Manager):
    def get_custom_queryset(self, today=None):
        queryset = super(EventManager, self).get_queryset()

        if not today:
            today = timezone.now()

        datetime_queryset = EventDatetime.objects \
            .filter(
                Q(event=OuterRef('pk')),
                Q(active=True),
                Q(datetime__gte=today) | Q(datetime__date__gte=today.date(), event__time_by_agreement=True)) \
            .values('datetime') \
            .order_by('datetime')
        queryset = queryset.annotate(datetime=Subquery(datetime_queryset[:1])) \
            .select_related('template') \
            .prefetch_related('template__images') \
            .filter(datetime__isnull=False) \
            .order_by('datetime', '-id')

        return queryset

    def get_archive_queryset(self, today=None):
        queryset = super(EventManager, self).get_queryset()

        if not today:
            today = timezone.now()

        datetime_queryset = EventDatetime.objects \
            .filter(
                Q(event=OuterRef('pk')),
                Q(active=True)) \
            .values('datetime') \
            .order_by('datetime')
        queryset = queryset.annotate(datetime=Subquery(datetime_queryset[:1])) \
            .select_related('template') \
            .prefetch_related('template__images') \
            .filter(datetime__isnull=False) \
            .order_by('datetime', '-id')

        return queryset


class Event(TimestampsMixin):
    time_by_agreement = models.BooleanField('время по договоренности', default=False)
    comment = models.TextField('комментарий', max_length=2048, default='', blank=True)
    recursive = models.BooleanField('повторяющиеся', default=False)
    template = models.ForeignKey('clndr.Template', verbose_name='шаблон мероприятия',
                                 null=True, on_delete=models.SET_NULL)
    user = models.ForeignKey('account.User', null=True, related_name='events',
                             on_delete=models.SET_NULL)
    restrictions = models.ManyToManyField('clndr.Restriction', verbose_name='ограничения',
                                          blank=True)

    default_manager = models.Manager()
    objects = EventManager()

    class Meta(object):
        verbose_name = _('event')
        verbose_name_plural = _('events')

    def __str__(self):
        return self.template.name

    def get_absolute_url(self):
        return reverse('event_detail', kwargs={'pk': self.id})


class EventDatetime(TimestampsMixin):
    datetime = models.DateTimeField(_('date and time'), null=True)
    active = models.BooleanField(default=True)
    free = models.BooleanField('свободно', default=True)
    event = models.ForeignKey('clndr.Event', related_name='datetime_set',
                              on_delete=models.CASCADE)

    class Meta(object):
        verbose_name = _('datetime')
        verbose_name_plural = _('datetime set')
        ordering = ('datetime', )

    def __str__(self):
        return self.datetime.strftime("%d.%m.%Y")


class Member(TimestampsMixin):
    user = models.ForeignKey('account.User', null=True, related_name='members',
                              on_delete=models.CASCADE)
    event = models.ForeignKey('clndr.Event', null=True, related_name='members',
                              on_delete=models.CASCADE)
    datetime = models.ForeignKey('clndr.EventDatetime', null=True, related_name='members',
                                 on_delete=models.CASCADE)

    class Meta(object):
        verbose_name = _('member')
        verbose_name_plural = _('members')


class EventFeedback(TimestampsMixin):
    text = models.TextField('текст отзыва', default='', max_length=2048,
                            help_text='Не более 2048 символов.')
    show = models.BooleanField(default=False)    
    event = models.ForeignKey('clndr.Event', null=True, related_name='feedback',
                              on_delete=models.CASCADE)
    user = models.ForeignKey('account.User', null=True, related_name='+',
                              on_delete=models.CASCADE)

    class Meta(object):
        verbose_name = _('feedback')
        verbose_name_plural = _('feedback')


class Restriction(TimestampsMixin):
    text = models.CharField('текст', max_length=64, default='')
    description = models.TextField('описание', max_length=1024, default='')

    class Meta(object):
        verbose_name = 'ограничение'
        verbose_name_plural = 'ограничения'

    def __str__(self):
        return self.text
