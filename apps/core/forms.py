from django import forms
from django.forms import widgets

from apps.clndr.models import EventDatetime, EventFeedback


class EventSingUpForm(forms.Form):
    datetime = forms.ModelChoiceField(queryset=EventDatetime.objects.all())
    phone = forms.CharField()


class EventFeedbackForm(forms.ModelForm):
    # text = forms.CharField(label='Текст отзыва', widget=widgets.Textarea(attrs={
    #     'rows': 5
    # }), help_text='Не более 2048 символов.')

    class Meta(object):
        model = EventFeedback
        fields = ('text', )
        widgets = {
            'text': widgets.Textarea(attrs={
                'rows': 5
            })
        }
