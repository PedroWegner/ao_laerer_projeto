from django.template import Library

register = Library()


@register.filter
def convert_int(value):
    return int(value)
