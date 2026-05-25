from django import template
from core.models import Order

register = template.Library()


@register.inclusion_tag('partials/cart_dropdown.html', takes_context=True)
def cart_dropdown(context):
    request = context.get('request')
    user = getattr(request, 'user', None)
    items = []
    total = 0
    if user and user.is_authenticated:
        order = Order.objects.filter(user=user, ordered=False).first()
        if order:
            items = order.items.all()
            total = order.get_total()
    return {'items': items, 'total': total}
