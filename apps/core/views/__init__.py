from django.db.models import Q
from django.forms.widgets import HiddenInput
from django.http.response import HttpResponseRedirect
from django.utils import timezone
from django.views.generic import TemplateView
from django.views.generic.base import TemplateResponseMixin
from django.views.generic.detail import SingleObjectMixin
from django.views.generic.edit import ProcessFormView
from django.conf import settings
from django.db.models import Subquery

from apps.account.forms import RegistrationForm
from apps.clndr.models import Event, EventDatetime, EventFeedback, Member
from apps.core.forms import EventFeedbackForm, EventSingUpForm, EventSingDownForm
from apps.core.utils import clear_phone

from .mixins import MultiFormMixin
from  apps.clndr.models import Member


# Create your views here.
class ProcessMultipleFormsView(ProcessFormView):
    def get(self, request, *args, **kwargs):
        form_classes = self.get_form_classes()
        forms = self.get_forms(form_classes)
        return self.render_to_response(self.get_context_data(forms=forms))

    def post(self, request, *args, **kwargs):
        form_classes = self.get_form_classes()
        form_name = request.POST.get('action')
        if self._individual_exists(form_name):
            return self._process_individual_form(form_name, form_classes)
        elif self._group_exists(form_name):
            return self._process_grouped_forms(form_name, form_classes)
        else:
            return self._process_all_forms(form_classes)

    def _individual_exists(self, form_name):
        return form_name in self.form_classes

    def _group_exists(self, group_name):
        return group_name in self.grouped_forms
  
    def _process_individual_form(self, form_name, form_classes):
        forms = self.get_forms(form_classes, (form_name,))
        form = forms.get(form_name)
        if not form:
            return HttpResponseForbidden()
        elif form.is_valid():
            return self.forms_valid(forms, form_name)
        else:
            return self.forms_invalid(forms)

    def _process_grouped_forms(self, group_name, form_classes):
        form_names = self.grouped_forms[group_name]
        forms = self.get_forms(form_classes, form_names)
        if all([forms.get(form_name).is_valid() for form_name in form_names.values()]):
            return self.forms_valid(forms)
        else:
            return self.forms_invalid(forms)

    def _process_all_forms(self, form_classes):
        forms = self.get_forms(form_classes, None, True)
        if all([form.is_valid() for form in forms.values()]):
            return self.forms_valid(forms)
        else:
            return self.forms_invalid(forms)


class BaseMultipleFormsView(MultiFormMixin, ProcessMultipleFormsView):
    """
    A base view for displaying several forms.
    """


class MultiFormsView(TemplateResponseMixin, BaseMultipleFormsView):
    """
    A view for displaying several forms, and rendering a template response.
    """


class HomepageView(MultiFormsView):
    form_classes = {
        'registration': RegistrationForm,
    }

    template_name = 'core/homepage.html'

    def get_context_data(self, **kwargs):
        now = timezone.now()

        event_list = Event.objects.get_custom_queryset().filter(datetime_set__free=True).distinct()
        self.extra_context = {
            'upcoming_event_list': event_list[:3],
            'event_list': event_list
        }

        return super(HomepageView, self).get_context_data(**kwargs)


class EventDetailView(SingleObjectMixin, MultiFormsView):
    form_classes = {
        'singup': EventSingUpForm,
        'singdown': EventSingDownForm,
        'feedback': EventFeedbackForm
    }

    template_name = 'core/event_detail.html'
    extra_context = {}

    #queryset = Event.objects.get_custom_queryset()
    queryset = Event.objects.get_archive_queryset()

    def get(self, request, *args, **kwargs):
        self.object = self.get_object()
        self.extra_context.update({
            'object': self.object
        })
        return super(EventDetailView, self).get(request, *args, **kwargs)

    def post(self, request, *args, **kwargs):
        self.object = self.get_object()
        self.extra_context.update({
            'object': self.object
        })
        return super(EventDetailView, self).post(request, *args, **kwargs)

    def get_context_data(self, **kwargs):
        context_data = super(EventDetailView, self).get_context_data(**kwargs)

        member_list = self.object.members.filter(user_id=self.request.user.id,
                                                 datetime__datetime__gte=self.object.datetime)
        all_subscriptions_count = Member.objects.filter(user_id=self.request.user.id,
                                                 datetime__datetime__gte=timezone.now()).count()
        print(all_subscriptions_count)
        context_data['member_list'] = member_list
        context_data['so_many_subscriptions'] = all_subscriptions_count >= settings.MAX_SUBSCRIPTIONS
        context_data['MAX_SUBSCRIPTION'] = settings.MAX_SUBSCRIPTIONS
        context_data['show_singup_form'] = not member_list and self._get_datetime_queryset() and not context_data['so_many_subscriptions']

        context_data['feedback_list'] = EventFeedback.objects \
            .filter(Q(event=self.object), Q(show=True) | Q(show=False, user_id=self.request.user.id))
        context_data['now'] = timezone.now()
                 
        return context_data

    def create_singup_form(self, **kwargs):
        obj = self.get_object()
        form_class = self.form_classes['singup']
        form = form_class(**kwargs)

        datetime_queryset = self._get_datetime_queryset()
        form.fields['datetime'].queryset = datetime_queryset
        if len(datetime_queryset) == 1:
            form.fields['datetime'].initial = datetime_queryset[0]
            form.fields['datetime'].widget = HiddenInput()

        if self.request.user.is_authenticated:
            form.fields['phone'].initial = self.request.user.phone

        return form

    def singup_form_valid(self, form):
        datetime = form.cleaned_data['datetime']

        phone = clear_phone(form.cleaned_data['phone'])
        if phone != self.request.user.phone:
            self.request.user.phone = phone
            self.request.user.save()

        member = Member.objects.create(user=self.request.user,
                                       event=self.object,
                                       datetime=datetime)

        datetime.free = False
        datetime.save()

        return HttpResponseRedirect(self.object.get_absolute_url())

    def singdown_form_valid(self, form):
        member_objects = Member.objects.filter(user=self.request.user, event=self.object)
        if member_objects:
            EventDatetime.objects.filter(event=self.object, id__in=Subquery(member_objects.values('datetime'))).update(free=True)
            member_objects.delete()

        return HttpResponseRedirect(self.object.get_absolute_url())

    def feedback_form_valid(self, form):
        text = form.cleaned_data['text']

        EventFeedback.objects.create(user=self.request.user,
                                     event=self.object,
                                     text=text)
        return HttpResponseRedirect(self.object.get_absolute_url())

    def _get_datetime_queryset(self):
        obj = self.get_object()
        return obj.datetime_set.filter(datetime__gte=obj.datetime, free=True)
