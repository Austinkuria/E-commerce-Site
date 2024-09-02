from django.contrib import admin
from .models import Product, Cart, CartItem, Order, OrderItem, ShippingDetails, Profile

class ProductAdmin(admin.ModelAdmin):
    list_display = ('name', 'price', 'image_tag', 'rating')  # Fields displayed in the list view
    search_fields = ('name',)  # Search by product name
    list_filter = ('price', 'rating')  # Filter products by price and rating
    ordering = ('-price',)  # Default order by price, descending

    def image_tag(self, obj):
        if obj.image:
            return f'<img src="{obj.image.url}" width="100" height="100" />'
        return 'No image'
    image_tag.allow_tags = True
    image_tag.short_description = 'Image'

class CartAdmin(admin.ModelAdmin):
    list_display = ('user', 'created_at')  # Display user and creation date
    search_fields = ('user__username',)  # Search by username

class CartItemAdmin(admin.ModelAdmin):
    list_display = ('cart', 'product', 'quantity')  # Display cart, product, and quantity
    search_fields = ('cart__user__username', 'product__name')  # Search by cart's user and product name

class OrderAdmin(admin.ModelAdmin):
    list_display = ('user', 'total', 'created_at')  # Display user, total amount, and creation date
    search_fields = ('user__username',)  # Search by username

class OrderItemAdmin(admin.ModelAdmin):
    list_display = ('order', 'product', 'quantity')  # Display order, product, and quantity
    search_fields = ('order__user__username', 'product__name')  # Search by order's user and product name

class ShippingDetailsAdmin(admin.ModelAdmin):
    list_display = ('order', 'address', 'city', 'postal_code')  # Display order, address, city, and postal code
    search_fields = ('order__user__username', 'address')  # Search by order's user and address
    ordering = ('-order',)  # Order by the order field in descending order

class ProfileAdmin(admin.ModelAdmin):
    list_display = ('user', 'phone_number', 'address', 'city', 'postal_code') # Display user, phone number,address, city, and postsl code
    search_fields = ('user__username', 'phone_number')  # Search by username and phone number

# Register models with the admin site
admin.site.register(Product, ProductAdmin)
admin.site.register(Cart, CartAdmin)
admin.site.register(CartItem, CartItemAdmin)
admin.site.register(Order, OrderAdmin)
admin.site.register(OrderItem, OrderItemAdmin)
admin.site.register(ShippingDetails, ShippingDetailsAdmin)
admin.site.register(Profile, ProfileAdmin)
class MyAdminSite(admin.AdminSite):
    site_header = 'My E-Commerce Admin'
    site_title = 'E-Commerce Admin Portal'
    index_title = 'Welcome to the E-Commerce Admin Dashboard'
    site_url = '/'

    def get_urls(self):
        urls = super().get_urls()
        custom_urls = [
            path('dashboard/', self.admin_view(custom_admin_dashboard), name='custom_admin_dashboard'),
        ]
        return custom_urls + urls

    def index(self, request, extra_context=None):
        extra_context = extra_context or {}
        extra_context['custom_dashboard_url'] = 'custom_admin_dashboard'
        return super().index(request, extra_context=extra_context)

admin_site = MyAdminSite(name='myadmin')

# Register models with the custom admin site
admin_site.register(Product, ProductAdmin)
admin_site.register(Cart, CartAdmin)
admin_site.register(CartItem, CartItemAdmin)
admin_site.register(Order, OrderAdmin)
admin_site.register(OrderItem, OrderItemAdmin)
admin_site.register(ShippingDetails, ShippingDetailsAdmin)
admin_site.register(Profile, ProfileAdmin)