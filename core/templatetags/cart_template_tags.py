from core.models import Order
from django import template

register = template.Library()


@register.filter
def cart_item_count(user):
    if user.is_authenticated:
        qs = Order.objects.filter(user_id=user, ordered=False)
        if qs.exists():
            return qs[0].order_lines.count()
    return 0
