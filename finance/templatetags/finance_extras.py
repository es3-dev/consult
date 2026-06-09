import json

from django import template
from django.core.serializers.json import DjangoJSONEncoder

register = template.Library()


@register.filter
def money(value):
    try:
        return f"${float(value):,.0f}"
    except (TypeError, ValueError):
        return "$0"


@register.filter
def as_json(value):
    return json.dumps(value, cls=DjangoJSONEncoder)
