from django import template
from django.utils.importlib import import_module


register = template.Library()


@register.filter(name="get_username")
def get_username(value):
    from userprofile.models import User
    return User.objects.get(id=int(value)).username