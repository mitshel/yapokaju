from django import forms
from django import template

from apps.core.utils import format_phone

register = template.Library()


@register.filter(name='is_checkbox_sm')
def is_checkbox_sm(field):
    """
    Boolean filter for form fields to determine if a field is using a checkbox
    widget.
    """
    return isinstance(field.field.widget, forms.CheckboxSelectMultiple)


@register.filter(name='is_radioselect')
def is_radioselect_filter(field):
    """
    Boolean filter for form fields to determine if a field is using a radioselect
    widget.
    """
    return isinstance(field.field.widget, forms.RadioSelect)


@register.filter(name='is_date')
def is_date_filter(field):
    """
    Boolean filter for form fields to determine if a field is using a dateinput
    widget.
    """
    return isinstance(field.field.widget, forms.DateInput)


@register.filter(name='phone')
def phone_filter(string):
    
    return format_phone(string)
