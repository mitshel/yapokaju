from datetime import datetime

from betterforms.forms import BetterForm, BetterModelForm, Fieldset
from betterforms.multiform import MultiForm
from django import forms
from django.contrib.auth.forms import PasswordChangeForm, UserChangeForm
from django.forms import widgets
from django.utils import timezone
from django.utils.text import capfirst, mark_safe
from django.utils.translation import ugettext_lazy as _
from registration.forms import RegistrationForm as BaseRegistrationForm

from apps.clndr.models import Event, EventDatetime, Restriction, Template

from .models import User


class RegistrationForm(BaseRegistrationForm):
    first_name = forms.CharField(label=capfirst(_('first name')), max_length=32)
    last_name = forms.CharField(label=capfirst(_('last name')), max_length=32)
    password1 = forms.CharField(
        label=_("Password"),
        strip=False,
        widget=widgets.PasswordInput,
        help_text=' '.join([
            'Ваш пароль должен содержать как минимум 8 символов',
            'и не должен состоять только из цифр.'
        ])
    )
    is_volunteer = forms.BooleanField(
        label='Я волонтер',
        help_text='Могу организовывать и проводить мероприятия.',
        required=False)

    def __init__(self, *args, **kwargs):
        super(RegistrationForm, self).__init__(*args, **kwargs)
        self.fields.move_to_end('email')
        self.fields.move_to_end('is_volunteer')
        self.fields.move_to_end('password1')
        self.fields.move_to_end('password2')

        self.fields['email'].widget.attrs.pop('autofocus', None)

    def save(self, commit=True):
        user = super(RegistrationForm, self).save(commit=False)
        user.first_name = self.cleaned_data['first_name']
        user.last_name = self.cleaned_data['last_name']
        user.is_volunteer = self.cleaned_data['is_volunteer']
        
        return super(RegistrationForm, self).save()



class ProfileForm(forms.ModelForm):
    class Meta(object):
        model = User
        fields = ('first_name', 'last_name', 'email')


class EventCreateStepFirstForm(BetterModelForm):
    class Meta(object):
        model = Event
        fields = ('template', 'recursive')
        widgets = {
            'recursive': widgets.RadioSelect(choices=[
                (False, 'Нет'),
                (True, 'Да')
            ]),
        }
    def __init__(self, *args, **kwargs):
        super(EventCreateStepFirstForm, self).__init__(*args, **kwargs)

        template_list = Template.objects.all()
        self.fields['template'].help_text = mark_safe(''.join([
            *[
                '<span class="template-file-href href-{}"><a href="{}">Скачать файл</a> с описанием экскурсии.</span>'.format(
                    t.id,
                    t.file.url,
                )
                for t in template_list if t.file]
        ]))


class EventCreateStepOnceForm(BetterForm):
    date = forms.DateField(label='Дата', widget=widgets.DateInput(attrs={
        'placeholder': '2019-12-31'
    }, format='%Y-%m-%d'))
    time = forms.TimeField(label='Время', widget=widgets.TimeInput(attrs={
        'placeholder': '00:00'
    }), help_text='Время московское.', required=False)
    time_by_agreement = forms.BooleanField(label='Время по договоренности',
                                           label_suffix='',
                                           required=False, initial=True)
    comment = forms.CharField(
        label='Комментарий',
        max_length=2048,
        widget=widgets.Textarea(attrs={
            'rows': 5
        }),
        required=False)
    restrictions = forms.ModelMultipleChoiceField(
        label='Ограничения',
        queryset=Restriction.objects.all(),
        widget=widgets.CheckboxSelectMultiple,
        required=False)

    class Media(object):
        js = (
            'core/js/bootstrap-datepicker.min.js',
            'core/js/bootstrap-datepicker.ru.min.js'
        )

    def __init__(self, *args, **kwargs):
        super(EventCreateStepOnceForm, self).__init__(*args, **kwargs)
        today = timezone.now()

        self.fields['time'].help_text = ' '.join([
            'Текущее время:',
            #timezone.localtime(today).strftime("%H:%M"),
            today.strftime("%H:%M"),
        ])


class EventCreateStepRepeatedlyForm(BetterForm):
    rrule = forms.CharField(widget=widgets.HiddenInput)
    time = forms.TimeField(label='Время', widget=widgets.TimeInput(attrs={
        'placeholder': '00:00'
    }), help_text='Время московское.', required=False)
    time_by_agreement = forms.BooleanField(label='Время по договоренности',
                                           label_suffix='',
                                           required=False, initial=True)
    comment = forms.CharField(
        label='Комментарий',
        max_length=2048,
        widget=widgets.Textarea(attrs={
            'rows': 5
        }),
        required=False)
    restrictions = forms.ModelMultipleChoiceField(
        label='Ограничения',
        queryset=Restriction.objects.all(),
        widget=widgets.CheckboxSelectMultiple,
        required=False)
    freq_type = forms.CharField(label='Количество повторений', widget=widgets.RadioSelect(choices=[
        ('f', 'Повторять максимальное количество раз'),
        ('c', 'Задать количество повторений'),
    ]), help_text='Будет создано не более 10 повторов события.', initial='f')
    freq_count = forms.IntegerField(label='Количество повторений', initial=10, required=False)
    repeat_type = forms.ChoiceField(label='Вариант повтора', choices=[
        ('d', 'Ежедневно'),
        ('w', 'Еженедельно'),
        ('mday', 'Ежемесячно, по дням месяца'),
        ('mdate', 'Ежемесячно, по числам месяца'),
        ('yday', 'Ежегодно, по дням месяца'),
        ('ydate', 'Ежегодно, по числам месяца'),
    ], initial='d')
    interval_daily = forms.ChoiceField(label='Интервал', choices=[
        ('1', 'Каждый день'),
        ('2', 'Через день'),
        ('3', 'Каждый 3-й день'),
        ('4', 'Каждый 4-ый день'),
        ('5', 'Каждый 5-ый день'),
        ('6', 'Каждый 6-ой день'),
        ('7', 'Каждый 7-ой день'),
        ('8', 'Каждый 8-ой день'),
        ('9', 'Каждый 9-ый день'),
        ('10', 'Каждый 10-ый день'),
        ('11', 'Каждый 11-ый день'),
        ('12', 'Каждый 12-ый день'),
        ('13', 'Каждый 13-ый день'),
        ('14', 'Каждый 14-ый день'),
        ('15', 'Каждый 15-ый день'),
        ('16', 'Каждый 16-ый день'),
        ('17', 'Каждый 17-ый день'),
        ('18', 'Каждый 18-ый день'),
        ('19', 'Каждый 19-ый день'),
        ('20', 'Каждый 20-ый день'),
        ('21', 'Каждый 21-ый день'),
        ('22', 'Каждый 22-ой день'),
        ('23', 'Каждый 23-ий день'),
        ('24', 'Каждый 24-ый день'),
        ('25', 'Каждый 25-ый день'),
        ('26', 'Каждый 26-ой день'),
        ('27', 'Каждый 27-ой день'),
        ('28', 'Каждый 28-ой день'),
        ('29', 'Каждый 29-ый день'),
        ('30', 'Каждый 30-ый день'),
    ], initial='1', required=False)
    repeat_weeklyday = forms.MultipleChoiceField(label='День недели', choices=[
        ('MO', 'Понедельник'),
        ('TU', 'Вторник'),
        ('WE', 'Среда'),
        ('TH', 'Четверг'),
        ('FR', 'Пятница'),
        ('SA', 'Суббота'),
        ('SU', 'Воскресенье'),
    ], required=False)
    interval_monthly = forms.ChoiceField(label='Повтор', choices=[
        ('1', 'Каждый месяц'),
        ('2', 'Через месяц'),
        ('3', 'Каждый 3-ий месяц'),
        ('4', 'Каждый 4-ый месяц'),
        ('5', 'Каждый 5-ый месяц'),
        ('6', 'Каждый 6-ой месяц'),
        ('7', 'Каждый 7-ой месяц'),
        ('8', 'Каждый 8-ой месяц'),
        ('9', 'Каждый 9-ый месяц'),
        ('10', 'Каждый 10-ый месяц'),
        ('11', 'Каждый 11-ый месяц'),
        ('12', 'Каждый 12-ый месяц'),
        ('24', 'Каждый 24-ый месяц'),
        ('36', 'Каждый 36-ой месяц'),
        ('48', 'Каждый 48-ой месяц'),
    ], initial='1', required=False)
    interval_weekly = forms.ChoiceField(label='Интервал', choices=[
        ('1', 'Каждую неделю'),
        ('2', 'Через неделю'),
        ('3', 'Каждую 3-ю неделю'),
        ('4', 'Каждую 4-ую неделю'),
        ('5', 'Каждую 5-ую неделю'),
        ('6', 'Каждую 6-ую неделю'),
        ('7', 'Каждую 7-ую неделю'),
        ('8', 'Каждую 8-ую неделю'),
        ('9', 'Каждую 9-ую неделю'),
        ('10', 'Каждую 10-ую неделю'),
        ('11', 'Каждую 11-ую неделю'),
        ('12', 'Каждую 12-ую неделю'),
        ('13', 'Каждую 13-ую неделю'),
        ('14', 'Каждую 14-ую неделю'),
        ('15', 'Каждую 15-ую неделю'),
        ('16', 'Каждую 16-ую неделю'),
        ('17', 'Каждую 17-ую неделю'),
        ('18', 'Каждую 18t-ую неделю'),
        ('19', 'Каждую 19-ую неделю'),
        ('20', 'Каждую 20-ую неделю'),
        ('21', 'Каждую 21-ую неделю'),
        ('22', 'Каждую 22-ую неделю'),
        ('23', 'Каждую 23-ую неделю'),
        ('24', 'Каждую 24-ую неделю'),
        ('25', 'Каждую 25-ую неделю'),
        ('26', 'Каждую 26-ую неделю'),
    ], required=False)
    interval_yearly = forms.ChoiceField(label='Интервал', choices=[
        ('1', 'Каждый год'),
        ('2', 'Через год'),
        ('3', 'Каждый 3-ий год'),
        ('4', 'Каждый 4-ый год'),
        ('5', 'Каждый 5-ый год'),
        ('6', 'Каждый 6-ой год'),
        ('7', 'Каждый 7-ой год'),
        ('8', 'Каждый 8-ой год'),
        ('9', 'Каждый 9-ый год'),
        ('10', 'Каждый 10-ый год'),
    ], required=False)
    repeat_yearly_month = forms.ChoiceField(label='Повтор', choices=[
        ('01', 'Январь'),
        ('02', 'Февраль'),
        ('03', 'Март'),
        ('04', 'Апрель'),
        ('05', 'Май'),
        ('06', 'Июнь'),
        ('07', 'Июль'),
        ('08', 'Август'),
        ('09', 'Сентябрь'),
        ('10', 'Октябрь'),
        ('11', 'Ноябрь'),
        ('12', 'Декабрь'),
    ], required=False)
    repeat_monthlydate = forms.MultipleChoiceField(label='Число месяца', choices=[
        ('1', '1-ый день'),
        ('2', '2-ой день'),
        ('3', '3-ий день'),
        ('4', '4-ый день'),
        ('5', '5-ый день'),
        ('6', '6-ой день'),
        ('7', '7-ой день'),
        ('8', '8-ой день'),
        ('9', '9-ый день'),
        ('10', '10-ый день'),
        ('11', '11-ый день'),
        ('12', '12-ый день'),
        ('13', '13-ый день'),
        ('14', '14-ый день'),
        ('15', '15-ый день'),
        ('16', '16-ый день'),
        ('17', '17-ый день'),
        ('18', '18-ый день'),
        ('19', '19-ый день'),
        ('20', '20-ый день'),
        ('21', '21-ый день'),
        ('22', '22-ой день'),
        ('23', '23-ий день'),
        ('24', '24-ый день'),
        ('25', '25-ый день'),
        ('26', '26-ой день'),
        ('27', '27-ой день'),
        ('28', '28-ой день'),
        ('29', '29-ый день'),
        ('30', '30-ый день'),
        ('31', '31-ый день'),
    ], required=False)
    repeat_monthlyday = forms.MultipleChoiceField(label='День месяца', choices=[
        ('1MO', '1-ый понедельник'),
        ('1TU', '1-ый вторник'),
        ('1WE', '1-я среда'),
        ('1TH', '1-ый четверг'),
        ('1FR', '1-я пятница'),
        ('1SA', '1-я суббота'),
        ('1SU', '1-ое воскресенье'),
        ('2MO', '2-ой понедельник'),
        ('2TU', '2-ой вторник'),
        ('2WE', '2-ая среда'),
        ('2TH', '2-ой четверг'),
        ('2FR', '2-ая пятница'),
        ('2SA', '2-ая суббота'),
        ('2SU', '2-ое воскресенье'),
        ('3MO', '3-ий понедельник'),
        ('3TU', '3-ий вторник'),
        ('3WE', '3-я среда'),
        ('3TH', '3-ий четверг'),
        ('3FR', '3-я пятница'),
        ('3SA', '3-я суббота'),
        ('3SU', '3-е воскресенье'),
        ('4MO', '4-ый понедельник'),
        ('4TU', '4-ый вторник'),
        ('4WE', '4-ая среда'),
        ('4TH', '4-ый четверг'),
        ('4FR', '4-ая пятница'),
        ('4SA', '4-ая суббота'),
        ('4SU', '4-ое воскресенье'),
        ('5MO', '5-ый понедельник'),
        ('5TU', '5-ый вторник'),
        ('5WE', '5-ая среда'),
        ('5TH', '5-ый четверг'),
        ('5FR', '5-ая пятница'),
        ('5SA', '5-ая суббота'),
        ('5SU', '5-ое воскресенье'),
        ('-1MO', 'Последний понедельник'),
        ('-1TU', 'Последний вторник'),
        ('-1WE', 'Последний среда'),
        ('-1TH', 'Последний четверг'),
        ('-1FR', 'Последний пятница'),
        ('-1SA', 'Последний суббота'),
        ('-1SU', 'Последний воскресенье'),
    ], required=False)

    class Media(object):
        js = ('core/js/rrule.js', )

    class Meta(object):
        fieldsets = (
            Fieldset('main', fields=('time', 'time_by_agreement', 'comment', 'restrictions', 'rrule')),
            Fieldset('repeat', fields=('repeat_type', )),
            Fieldset('rule d', fields=('interval_daily', )),
            Fieldset('rule w', fields=('interval_weekly', 'repeat_weeklyday')),
            Fieldset('rule mday mdate', fields=('interval_monthly', )),
            Fieldset('rule yday ydate', fields=('interval_yearly', 'repeat_yearly_month')),
            Fieldset('rule mday yday', fields=('repeat_monthlyday', )),
            Fieldset('rule mdate ydate', fields=('repeat_monthlydate', )),
            Fieldset('freq_type', fields=('freq_type', )),
            Fieldset('freq c', fields=('freq_count', )),
        )

    def __init__(self, *args, **kwargs):
        super(EventCreateStepRepeatedlyForm, self).__init__(*args, **kwargs)
        today = timezone.now()

        self.fields['time'].help_text = ' '.join([
            'Текущее время:',
            #timezone.localtime(today).strftime("%H:%M"),
            today.strftime("%H:%M"),
        ])


class EventDatetimeForm(forms.ModelForm):
    datetime = forms.SplitDateTimeField(widget=widgets.SplitDateTimeWidget(
        date_attrs={
            'class': 'form-control datepicker'
        },
        time_attrs={
            'class': 'form-control mt-1'
        },
        date_format='%Y-%m-%d',
        time_format='%H-%M'
    ))
    class Meta(object):
        model = EventDatetime
        fields = ('datetime', 'free')

    class Media(object):
        js = (
            'core/js/bootstrap-datepicker.min.js',
            'core/js/bootstrap-datepicker.ru.min.js'
        )

    def __init__(self, *args, **kwargs):
        super(EventDatetimeForm, self).__init__(*args, **kwargs)
        today = timezone.now()

        self.fields['datetime'].help_text = ' '.join([
            'Текущяя дата и время:',
            today.strftime("%d.%m.%Y %H:%M"),
            #timezone.localtime(today).strftime("%d.%m.%Y %H:%M МСК"),
        ])



class EventChangeForm(BetterModelForm):
    comment = forms.CharField(
        label='Комментарий',
        max_length=2048,
        widget=widgets.Textarea(attrs={
            'rows': 5
        }),
        required=False)
    time_by_agreement = forms.BooleanField(label='Время по договоренности',
                                           label_suffix='',
                                           required=False)

    class Meta(object):
        model = Event
        fields = ('comment', 'restrictions', 'time_by_agreement')
        widgets = {
            'restrictions': widgets.CheckboxSelectMultiple
        }
