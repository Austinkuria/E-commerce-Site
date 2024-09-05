from django import views
from django.contrib import admin
from .models import Product, Cart, CartItem, Order, OrderItem, ShippingDetails, Profile, SalesReport

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

class SalesReportAdmin(admin.ModelAdmin):
    list_display = ('product', 'quantity_sold', 'total_revenue', 'report_date')
    list_filter = ('report_date', 'product')
    search_fields = ('product__name',)

# Register models with the admin site
admin.site.register(Product, ProductAdmin)
admin.site.register(Cart, CartAdmin)
admin.site.register(CartItem, CartItemAdmin)
admin.site.register(Order, OrderAdmin)
admin.site.register(OrderItem, OrderItemAdmin)
admin.site.register(ShippingDetails, ShippingDetailsAdmin)
admin.site.register(Profile, ProfileAdmin)
admin.site.register(SalesReport, SalesReportAdmin)
