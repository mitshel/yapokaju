from datetime import datetime

from dateutil.rrule import rrule, rrulestr
from django.contrib.auth.forms import PasswordChangeForm
from django.contrib.auth.mixins import LoginRequiredMixin
from django.http.response import HttpResponseRedirect
from django.shortcuts import render
from django.urls import reverse_lazy
from django.utils import timezone
from django.views.generic import FormView, ListView, TemplateView
from formtools.wizard.views import SessionWizardView
from registration.views import RegistrationView as BaseRegistrationView

from apps.clndr.models import Event, EventDatetime
from apps.core.views import MultiFormsView

from .forms import (EventCreateStepFirstForm, EventCreateStepOnceForm,
                    EventCreateStepRepeatedlyForm, ProfileForm)


# Create your views here.
class ProfileView(LoginRequiredMixin, TemplateView):
    template_name = 'account/profile.html'


class ProfileSettingsView(LoginRequiredMixin, MultiFormsView):
    form_classes = {
        'profile': ProfileForm,
        'password': PasswordChangeForm
    }
    success_url = reverse_lazy('profile_settings')

    template_name = 'account/settings.html'

    def get_form_kwargs(self, form_name, bind_form=False):
        kwargs = super(ProfileSettingsView, self).get_form_kwargs(form_name, bind_form)
        user = self.request.user
        if form_name == 'profile':
            kwargs.update({
                'instance': user
            })
        if form_name == 'password':
            kwargs.update({
                'user': user
            })
        return kwargs

    def profile_form_valid(self, form):
        form.save()
        return HttpResponseRedirect(self.get_success_url())

    def password_form_valid(self, form):
        form.save()
        return HttpResponseRedirect(self.get_success_url())


class ProfileEventListView(LoginRequiredMixin, ListView):
    queryset = Event.objects.all()

    template_name = 'account/event_list.html'

    def get_queryset(self):
        queryset = super(ProfileEventListView, self).get_queryset()
        queryset = queryset.filter(user=self.request.user)
        return queryset


EVENT_CREATE_TEMPLATES = {
    'main': 'account/event_create_step_main.html',
    'once': 'account/event_create_step_once.html',
    'repeatedly': 'account/event_create_step_repeatedly.html',
}


def once_event(wizard):
    cleaned_data = wizard.get_cleaned_data_for_step('main')
    if not cleaned_data:
        return False
    return cleaned_data.get('recursive', False) == False


def repeatedly_event(wizard):
    cleaned_data = wizard.get_cleaned_data_for_step('main')
    if not cleaned_data:
        return False
    return cleaned_data.get('recursive', False)


class ProfileEventCreateView(LoginRequiredMixin, SessionWizardView):
    form_list = [
        ('main', EventCreateStepFirstForm),
        ('once', EventCreateStepOnceForm),
        ('repeatedly', EventCreateStepRepeatedlyForm)
    ]

    condition_dict = {
        'once': once_event,
        'repeatedly': repeatedly_event
    }

    success_url = reverse_lazy('profile_event_list')

    def get_form_initial(self, step):
        today = timezone.now()
        self.initial_dict = {
            'once': {
                'date': today.date(),
                'time': today.time()
            },
            'repeatedly': {
                'time': today.time()
            }
        }
        return super(ProfileEventCreateView, self).get_form_initial(step)

    def get_template_names(self):
        return [EVENT_CREATE_TEMPLATES[self.steps.current]]

    def get_success_url(self):
        """Return the URL to redirect to after processing a valid form."""
        if not self.success_url:
            raise ImproperlyConfigured("No URL to redirect to. Provide a success_url.")
        return str(self.success_url)
    
    def done(self, form_list, **kwargs):
        main_step_cleaned_data = self.get_cleaned_data_for_step('main')

        event = Event.objects.create(template=main_step_cleaned_data['template'],
                                     recursive=main_step_cleaned_data['recursive'],
                                     user=self.request.user)


        datetime_list = []
        if main_step_cleaned_data['recursive']:
            repeatedly_step_cleaned_data = self.get_cleaned_data_for_step('repeatedly')

            rrule_str = repeatedly_step_cleaned_data['rrule']
            if not 'COUNT' in rrule_str:
                rrule_str += ';COUNT=10'
            for datetime_instance in rrulestr(rrule_str):
                datetime_instance = datetime_instance.replace(
                    hour=repeatedly_step_cleaned_data['time'].hour,
                    minute=repeatedly_step_cleaned_data['time'].minute,
                    second=0, microsecond=0
                )
                datetime_list.append(EventDatetime(datetime=datetime_instance, event=event))
        else:
            oncey_step_cleaned_data = self.get_cleaned_data_for_step('once')

            datetime_list.append(EventDatetime(
                datetime=datetime.combine(
                    oncey_step_cleaned_data['date'],
                    oncey_step_cleaned_data['time']
                ),
                event=event))

        EventDatetime.objects.bulk_create(datetime_list)

        return HttpResponseRedirect(self.get_success_url())


class ProfileReviewListView(LoginRequiredMixin, TemplateView):
    template_name = 'account/review_list.html'


class ProfileReviewCreateView(LoginRequiredMixin ,TemplateView):
    template_name = 'account/settings.html'
