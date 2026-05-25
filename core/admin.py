from django.contrib import admin

from .models import Item, OrderItem, Order, BillingAddress, Category, Slide, UserProfile


def copy_items(modeladmin, request, queryset):
    for obj in queryset:
        obj.pk = None
        obj.save()


copy_items.short_description = 'Duplicate selected items'


@admin.register(Item)
class ItemAdmin(admin.ModelAdmin):
    list_display = ['title', 'category', 'price',
                    'discount_price', 'label', 'is_active']
    list_filter = ['category', 'label', 'is_active']
    search_fields = ['title', 'description_short']
    prepopulated_fields = {'slug': ('title',)}
    list_editable = ['is_active', 'price', 'discount_price']
    actions = [copy_items]


@admin.register(Category)
class CategoryAdmin(admin.ModelAdmin):
    list_display = ['title', 'slug', 'is_active']
    list_filter = ['is_active']
    search_fields = ['title']
    prepopulated_fields = {'slug': ('title',)}
    list_editable = ['is_active']


@admin.register(Slide)
class SlideAdmin(admin.ModelAdmin):
    list_display = ['caption1', 'caption2', 'is_active']
    list_editable = ['is_active']


@admin.register(Order)
class OrderAdmin(admin.ModelAdmin):
    list_display = ['user', 'ref_code', 'ordered',
                    'being_delivered', 'received', 'billing_address']
    list_display_links = ['user', 'billing_address']
    list_filter = ['ordered', 'being_delivered', 'received']
    search_fields = ['user__username', 'ref_code']


@admin.register(OrderItem)
class OrderItemAdmin(admin.ModelAdmin):
    list_display = ['item', 'user', 'quantity', 'ordered']
    list_filter = ['ordered']
    search_fields = ['item__title', 'user__username']


@admin.register(BillingAddress)
class AddressAdmin(admin.ModelAdmin):
    list_display = ['user', 'street_address', 'apartment_address',
                    'country', 'zip', 'address_type', 'default']
    list_filter = ['default', 'address_type', 'country']
    search_fields = ['user__username', 'street_address', 'zip']


@admin.register(UserProfile)
class UserProfileAdmin(admin.ModelAdmin):
    list_display = ['user', 'phone', 'address']
    search_fields = ['user__username', 'user__email']
