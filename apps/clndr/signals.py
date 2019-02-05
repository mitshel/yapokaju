from django.conf import settings
from django.core.mail import EmailMessage, send_mail
from django.db.models.signals import post_save
from django.dispatch import Signal, receiver
from django.utils import timezone

from apps.core.utils import format_phone

from .models import Member


@receiver(post_save, sender=Member)
def send_mail_to_organizer(sender, instance, created, **kwargs):
    if created:
        subject = 'Подписка на мероприятие'
        text = ' '.join([
            'Уважаемый ВОЛОНТЕР.'
            'На Ваше мероприятие',
            '"' + instance.event.template.name + '"',
            'запланированное время:',
            timezone.localtime(instance.datetime.datetime).strftime('%d.%m.%Y г. в %H:%M (МСК)'),
            'подписался(лась)',
            instance.user.get_full_name(),
            instance.user.email,
            format_phone(instance.user.phone),'\n',
            'Пожалуйста свяжитесь с человеком, которому требуется Ваша помощь по указанному телефону, для обсуждения деталей экскурсии'
        ])
        email = EmailMessage(subject, text, settings.DEFAULT_FROM_EMAIL, [instance.event.user.email, ])
        email.send()
