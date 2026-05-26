from django.contrib import messages
from django.core.exceptions import ObjectDoesNotExist
from django.contrib.auth.decorators import login_required
from django.contrib.auth.mixins import LoginRequiredMixin
from django.http import JsonResponse
from django.shortcuts import render, get_object_or_404, redirect
from django.urls import reverse
from django.views.generic import ListView, DetailView, View
from django.utils import timezone
from .models import Item, OrderItem, Order, Category

# Create your views here.


class HomeView(ListView):
    template_name = "index.html"
    context_object_name = 'items'

    def get_queryset(self):
        return Item.objects.filter(is_active=True).select_related('category').order_by('-id')[:8]


class OrderSummaryView(LoginRequiredMixin, View):
    def get(self, *args, **kwargs):
        try:
            order = Order.objects.prefetch_related('items__item').get(
                user=self.request.user, ordered=False)
            context = {
                'object': order
            }
            return render(self.request, 'order_summary.html', context)
        except ObjectDoesNotExist:
            messages.error(self.request, "You do not have an active order")
            return redirect("/")


PRICE_RANGES = {
    'under100':      (None, 100),
    '100-500':       (100, 500),
    '500-5000':      (500, 5000),
    '5000-50000':    (5000, 50000),
    'above50000':    (50000, None),
}


class ShopView(ListView):
    paginate_by = 6
    template_name = "shop.html"
    context_object_name = 'items'

    def get_queryset(self):
        qs = Item.objects.filter(is_active=True).select_related('category')

        # Category
        cat_slug = self.request.GET.get('category', '').strip()
        if cat_slug:
            qs = qs.filter(category__slug=cat_slug)

        # Text search
        q = self.request.GET.get('q', '').strip()
        if q:
            qs = qs.filter(title__icontains=q)

        # Price range
        price_range = self.request.GET.get('price_range', '')
        if price_range in PRICE_RANGES:
            lo, hi = PRICE_RANGES[price_range]
            if lo is not None:
                qs = qs.filter(price__gte=lo)
            if hi is not None:
                qs = qs.filter(price__lte=hi)

        # Sort
        sort = self.request.GET.get('sort', 'default')
        if sort == 'price_asc':
            qs = qs.order_by('price')
        elif sort == 'price_desc':
            qs = qs.order_by('-price')
        elif sort == 'popular':
            # 'P' > 'N' so -label puts P first
            qs = qs.order_by('-label', 'title')
        else:
            qs = qs.order_by('title')

        return qs

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        context['current_sort'] = self.request.GET.get('sort', 'default')
        context['current_price_range'] = self.request.GET.get(
            'price_range', '')
        context['current_q'] = self.request.GET.get('q', '')
        context['current_category'] = self.request.GET.get('category', '')
        context['total_count'] = self.object_list.count()
        context['categories'] = Category.objects.filter(
            is_active=True).order_by('title')
        # Query string without 'page' — used to build paginator links
        params = self.request.GET.copy()
        params.pop('page', None)
        context['filter_params'] = params.urlencode()
        return context


class ItemDetailView(DetailView):
    model = Item
    template_name = "product-detail.html"


# class CategoryView(DetailView):
#     model = Category
#     template_name = "category.html"

class CategoryView(View):
    def get(self, *args, **kwargs):
        category = get_object_or_404(Category, slug=self.kwargs['slug'])
        qs = Item.objects.filter(
            category=category, is_active=True).select_related('category')

        q = self.request.GET.get('q', '').strip()
        if q:
            qs = qs.filter(title__icontains=q)

        price_range = self.request.GET.get('price_range', '')
        if price_range in PRICE_RANGES:
            lo, hi = PRICE_RANGES[price_range]
            if lo is not None:
                qs = qs.filter(price__gte=lo)
            if hi is not None:
                qs = qs.filter(price__lte=hi)

        sort = self.request.GET.get('sort', 'default')
        if sort == 'price_asc':
            qs = qs.order_by('price')
        elif sort == 'price_desc':
            qs = qs.order_by('-price')
        elif sort == 'popular':
            qs = qs.order_by('-label', 'title')
        else:
            qs = qs.order_by('title')

        params = self.request.GET.copy()
        params.pop('page', None)

        context = {
            'object_list': qs,
            'category_title': category,
            'category_description': category.description,
            'category_image': category.image,
            'current_sort': sort,
            'current_price_range': price_range,
            'current_q': q,
            'total_count': qs.count(),
            'categories': Category.objects.filter(is_active=True).order_by('title'),
            'current_category': category.slug,
            'filter_params': params.urlencode(),
        }
        return render(self.request, "category.html", context)


@login_required
def add_to_cart(request, slug):
    item = get_object_or_404(Item, slug=slug)
    is_ajax = request.headers.get('X-Requested-With') == 'XMLHttpRequest'
    order_item, created = OrderItem.objects.get_or_create(
        item=item,
        user=request.user,
        ordered=False
    )
    order_qs = Order.objects.filter(user=request.user, ordered=False)
    if order_qs.exists():
        order = order_qs[0]
        if created:
            msg = f"'{item.title}' added to your cart."
        else:
            order_item.quantity += 1
            order_item.save()
            msg = f"'{item.title}' qty updated."
        order.items.add(order_item)  # idempotent — safe even if already linked
    else:
        order = Order.objects.create(
            user=request.user, ordered_date=timezone.now())
        order.items.add(order_item)
        msg = f"'{item.title}' added to your cart."
    if is_ajax:
        order_item.refresh_from_db()
        return JsonResponse({
            'status': 'ok',
            'message': msg,
            'cart_count': order.items.count(),
            'new_quantity': order_item.quantity,
            'item_total': str(order_item.get_total_item_price()),
            'order_total': str(order.get_total()),
            'removed': False,
            'empty': False,
        })
    messages.success(request, msg)
    next_url = request.META.get('HTTP_REFERER') or reverse(
        'core:product', kwargs={'slug': slug})
    return redirect(next_url)


@login_required
def remove_from_cart(request, slug):
    item = get_object_or_404(Item, slug=slug)
    is_ajax = request.headers.get('X-Requested-With') == 'XMLHttpRequest'
    order_qs = Order.objects.filter(user=request.user, ordered=False)
    if order_qs.exists():
        order = order_qs[0]
        order_item = OrderItem.objects.filter(
            item=item, user=request.user, ordered=False).first()
        if order_item and order.items.filter(pk=order_item.pk).exists():
            order.items.remove(order_item)
            if is_ajax:
                order_total = order.get_total()
                return JsonResponse({
                    'status': 'ok',
                    'cart_count': order.items.count(),
                    'order_total': str(order_total) if order_total else '0.00',
                    'empty': order.items.count() == 0,
                })
            messages.info(request, "Item was removed from your cart.")
            return redirect("core:order-summary")
    if is_ajax:
        return JsonResponse({'status': 'error', 'message': 'Item not in cart'})
    messages.info(request, "Item was not in your cart.")
    return redirect("core:order-summary")


@login_required
def remove_single_item_from_cart(request, slug):
    item = get_object_or_404(Item, slug=slug)
    is_ajax = request.headers.get('X-Requested-With') == 'XMLHttpRequest'
    order_qs = Order.objects.filter(user=request.user, ordered=False)
    if order_qs.exists():
        order = order_qs[0]
        order_item = OrderItem.objects.filter(
            item=item, user=request.user, ordered=False).first()
        if order_item and order.items.filter(pk=order_item.pk).exists():
            if order_item.quantity > 1:
                order_item.quantity -= 1
                order_item.save()
                if is_ajax:
                    return JsonResponse({
                        'status': 'ok',
                        'removed': False,
                        'new_quantity': order_item.quantity,
                        'item_total': str(order_item.get_total_item_price()),
                        'cart_count': order.items.count(),
                        'order_total': str(order.get_total()),
                        'empty': False,
                    })
            else:
                order.items.remove(order_item)
                if is_ajax:
                    order_total = order.get_total()
                    return JsonResponse({
                        'status': 'ok',
                        'removed': True,
                        'cart_count': order.items.count(),
                        'order_total': str(order_total) if order_total else '0.00',
                        'empty': order.items.count() == 0,
                    })
            messages.info(request, "This item qty was updated.")
            return redirect("core:order-summary")
    if is_ajax:
        return JsonResponse({'status': 'error', 'message': 'Item not in cart'})
    messages.info(request, "Item was not in your cart.")
    return redirect("core:order-summary")
