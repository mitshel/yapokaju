from django import forms
from django.forms import widgets

from apps.clndr.models import EventDatetime, EventFeedback


class EventSingUpForm(forms.Form):
    datetime = forms.ModelChoiceField(queryset=EventDatetime.objects.all())
    phone = forms.CharField()


class EventFeedbackForm(forms.ModelForm):

    class Meta(object):
        model = EventFeedback
        fields = ('text', )
        widgets = {
            'text': widgets.Textarea(attrs={
                'rows': 5
            })
        }
