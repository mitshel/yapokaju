from django import forms
from django import template

register = template.Library()


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
