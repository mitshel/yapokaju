from django.conf import settings
from django.core.mail import EmailMessage, send_mail
from django.db.models.signals import post_save, pre_delete
from django.dispatch import Signal, receiver
from django.utils import timezone

from apps.core.utils import format_phone

from .models import Member


@receiver(post_save, sender=Member)
def send_mail_to_organizer(sender, instance, created, **kwargs):
    if created:
        subject = 'Подписка на мероприятие'
        text = ' '.join([
            'Уважаемый ВОЛОНТЕР.\nНа Ваше мероприятие',
            '"' + instance.event.template.name + '"',
            ', дата:',
            #timezone.localtime(instance.datetime.datetime).strftime('%d.%m.%Y'),
            instance.datetime.datetime.strftime('%d.%m.%Y'),
            ', подписался(лась)',
            instance.user.get_full_name()+'.',
            '\nE-mail:',
            instance.user.email,
            '\nТелефон:',
            format_phone(instance.user.phone),
            '\nПожалуйста, свяжитесь с человеком, которому требуется Ваша помощь,',
            'по указанному телефону или электронной почте, для обсуждения деталей экскурсии.'
        ])
        email = EmailMessage(subject, text, settings.DEFAULT_FROM_EMAIL, [instance.event.user.email, ])
        email.send()

@receiver(pre_delete, sender=Member)
def send_mail_to_organizer_delte(sender, instance, **kwargs):
    subject = 'Отмена подписка на мероприятие'
    text = ' '.join([
        'Уважаемый ВОЛОНТЕР.\nНа Ваше мероприятие',
        '"' + instance.event.template.name + '"',
        ', дата:',
        #timezone.localtime(instance.datetime.datetime).strftime('%d.%m.%Y'),
        instance.datetime.datetime.strftime('%d.%m.%Y'),
        ', была отменена подписка пользователем',
        instance.user.get_full_name()+'.',
        '\nE-mail:',
        instance.user.email,
        '\nТелефон:',
        format_phone(instance.user.phone)
    ])
    email = EmailMessage(subject, text, settings.DEFAULT_FROM_EMAIL, [instance.event.user.email, ])
    email.send()
