from django import template

register = template.Library()

@register.filter
def get_item(dictionary, key):
    """
    Dictionary'den key ile değer alma
    """
    return dictionary.get(key, '')

@register.filter
def add_string(value, arg):
    """
    String concatenation
    """
    return str(value) + str(arg)

@register.filter
def get_field(form, field_name):
    """
    Form'dan field_name ile field alma
    """
    return form[field_name]
