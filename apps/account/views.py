from datetime import datetime

from dateutil.rrule import rrule, rrulestr
from django.contrib.auth.forms import PasswordChangeForm
from django.contrib.auth.mixins import LoginRequiredMixin
from django.http.response import HttpResponseRedirect
from django.shortcuts import render
from django.urls import reverse_lazy
from django.utils import timezone
from django.views.generic import (DeleteView, DetailView, FormView, ListView,
                                  TemplateView, UpdateView)
from django.db.models import Max, Count
from extra_views import InlineFormSetFactory, UpdateWithInlinesView
from formtools.wizard.views import SessionWizardView
from registration.views import RegistrationView as BaseRegistrationView

from apps.clndr.models import Event, EventDatetime, Member
from apps.core.views import MultiFormsView

from .forms import (EventChangeForm, EventCreateStepFirstForm,
                    EventCreateStepOnceForm, EventCreateStepRepeatedlyForm,
                    EventDatetimeForm, ProfileForm)


# Create your views here.
class ProfileView(LoginRequiredMixin, TemplateView):
    template_name = 'account/profile.html'
    extra_context = {}

    def get_context_data(self, **kwargs):
        today = timezone.now()
        member_list = self.request.user.members.filter(datetime__datetime__gte=today)
        member_list_archive = self.request.user.members.filter(datetime__datetime__lt=today)
        self.extra_context = {
            'member_list': member_list,
            'member_list_archive': member_list_archive
        }

        return super(ProfileView, self).get_context_data(**kwargs)


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

    def create_password_form(self, **kwargs):
        form_class = self.form_classes['password']
        form = form_class(**kwargs)
        form.fields['old_password'].widget.attrs.pop('autofocus', None)
        return form

    def profile_form_valid(self, form):
        form.save()
        return HttpResponseRedirect(self.get_success_url())

    def password_form_valid(self, form):
        form.save()
        return HttpResponseRedirect(self.get_success_url())


class ProfileEventListView(LoginRequiredMixin, ListView):
    model = Event

    template_name = 'account/event_list.html'

    def get_queryset(self):
        queryset = super(ProfileEventListView, self).get_queryset()
        queryset = queryset.filter(user=self.request.user, datetime_set__isnull=False) \
                           .annotate(maxdate=Max('datetime_set__datetime')) \
                           .annotate(members_count = Count('members', distinct=True)) \
                           .order_by('-id').distinct()
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
            },
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
        today = timezone.now()
        main_step_cleaned_data = self.get_cleaned_data_for_step('main')

        event = Event.objects.create(template=main_step_cleaned_data['template'],
                                     recursive=main_step_cleaned_data['recursive'],
                                     user=self.request.user)

        datetime_list = []
        if main_step_cleaned_data['recursive']:
            repeatedly_step_cleaned_data = second_step_cleaned_data = self.get_cleaned_data_for_step('repeatedly')
            time_by_agreement = repeatedly_step_cleaned_data['time_by_agreement']

            rrule_str = repeatedly_step_cleaned_data['rrule']
            if not 'COUNT' in rrule_str:
                rrule_str += ';COUNT=10'
            for datetime_instance in rrulestr(rrule_str):
                if repeatedly_step_cleaned_data['time']:
                    datetime_instance = datetime_instance.replace(
                        hour=repeatedly_step_cleaned_data['time'].hour,
                        minute=repeatedly_step_cleaned_data['time'].minute,
                        second=0,
                        microsecond=0)
                if not repeatedly_step_cleaned_data['time'] or time_by_agreement:
                    datetime_instance = datetime_instance.replace(
                        hour=0,
                        minute=0,
                        second=0,
                        microsecond=0)

                datetime_list.append(EventDatetime(datetime=datetime_instance, event=event))
        else:
            oncey_step_cleaned_data = second_step_cleaned_data = self.get_cleaned_data_for_step('once')
            time_by_agreement = oncey_step_cleaned_data['time_by_agreement']

            datetime_instance = datetime.combine(
                oncey_step_cleaned_data['date'],
                today.time())

            if oncey_step_cleaned_data['time']:
                datetime_instance = datetime_instance.replace(
                    hour=oncey_step_cleaned_data['time'].hour,
                    minute=oncey_step_cleaned_data['time'].minute,
                    second=0,
                    microsecond=0)

            if not oncey_step_cleaned_data['time'] or time_by_agreement:
                    datetime_instance = datetime_instance.replace(
                        hour=0,
                        minute=0,
                        second=0,
                        microsecond=0)
            datetime_list.append(EventDatetime(datetime=datetime_instance, event=event))
        EventDatetime.objects.bulk_create(datetime_list)

        for restriction in second_step_cleaned_data['restrictions']:
            event.restrictions.add(restriction)

        event.comment = second_step_cleaned_data['comment']
        event.time_by_agreement = second_step_cleaned_data['time_by_agreement']
        event.save()

        return HttpResponseRedirect(self.get_success_url())


class ProfileEventDetailView(LoginRequiredMixin, DetailView):
    model = Event

    template_name = 'account/event_detail.html'

    def get_queryset(self):
        queryset = super(ProfileEventDetailView, self).get_queryset()
        queryset = queryset.filter(user=self.request.user)
        return queryset

    def get_context_data(self, **kwargs):
        obj = self.get_object()

        self.extra_context = {
            'member_list': obj.members.all()
        }

        return super(ProfileEventDetailView, self).get_context_data(**kwargs)


class EventDatetimeInline(InlineFormSetFactory):
    model = EventDatetime
    form_class = EventDatetimeForm
    
    factory_kwargs = {
        'extra': 0
    }


class ProfileEventChangeView(LoginRequiredMixin, UpdateWithInlinesView):
    model = Event
    inlines = [
        EventDatetimeInline,
    ]
    form_class = EventChangeForm

    template_name = 'account/event_change.html'

    def get_queryset(self):
        queryset = super(ProfileEventChangeView, self).get_queryset()
        queryset = queryset.filter(user=self.request.user)
        return queryset

    def get_success_url(self):
        obj = self.get_object()
        if not obj.datetime_set.all():
            return reverse_lazy('profile_event_list')
        return reverse_lazy('profile_event_change', kwargs={'pk': obj.id})


class ProfileEventDeleteView(LoginRequiredMixin, DeleteView):
    model = Event

    template_name = 'account/event_confirm_delete.html'

    def get_queryset(self):
        queryset = super(ProfileEventDeleteView, self).get_queryset()
        queryset = queryset.filter(user=self.request.user)
        return queryset

    def get_success_url(self):
        return reverse_lazy('profile_event_list')
