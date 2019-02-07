from django import forms
from django.forms import widgets
#from phonenumber_field.formfields import PhoneNumberField

from apps.clndr.models import EventDatetime, EventFeedback


class EventSingUpForm(forms.Form):
    datetime = forms.ModelChoiceField(queryset=EventDatetime.objects.all(),label='Дата')
    phone = forms.CharField(label='Телефон',)
    #phone = PhoneNumberField(label='Телефон')

class EventSingDownForm(forms.Form):
    pass

class EventFeedbackForm(forms.ModelForm):

    class Meta(object):
        model = EventFeedback
        fields = ('text', )
        widgets = {
            'text': widgets.Textarea(attrs={
                'rows': 5
            })
        }
