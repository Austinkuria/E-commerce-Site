from django.contrib import admin
from .models import Product, Cart, CartItem, Order, OrderItem, ShippingDetails, Payment, Profile

# Product Admin
class ProductAdmin(admin.ModelAdmin):
    list_display = ('name', 'price', 'image_tag', 'rating', 'stock')  # Display these fields in the list view
    search_fields = ('name',)  # Add a search bar for the 'name' field
    list_filter = ('price', 'rating')  # Add a filter sidebar by 'price' and 'rating'
    ordering = ('-price',)  # Optional: Order products by price, descending

    # Optionally, configure how the form is displayed on the admin page
    fields = ('name', 'price', 'description', 'rating', 'reviews', 'stock', 'image')  # Order fields as they appear in the admin form

    # Optionally, customize how the image field is displayed in the admin list view
    def image_tag(self, obj):
        if obj.image:
            return '<img src="%s" width="100" height="100" />' % obj.image.url
        return 'No image'
    image_tag.allow_tags = True
    image_tag.short_description = 'Image'

admin.site.register(Product, ProductAdmin)

# Cart Admin
class CartAdmin(admin.ModelAdmin):
    list_display = ('user', 'created_at')
    search_fields = ('user__username',)
    ordering = ('-created_at',)

admin.site.register(Cart, CartAdmin)

# CartItem Admin
class CartItemAdmin(admin.ModelAdmin):
    list_display = ('cart', 'product', 'quantity')
    search_fields = ('cart__user__username', 'product__name')
    ordering = ('-cart',)

admin.site.register(CartItem, CartItemAdmin)

# Order Admin
class OrderAdmin(admin.ModelAdmin):
    list_display = ('user', 'total_price', 'status', 'created_at')
    search_fields = ('user__username',)
    list_filter = ('status',)
    ordering = ('-created_at',)

admin.site.register(Order, OrderAdmin)

# OrderItem Admin
class OrderItemAdmin(admin.ModelAdmin):
    list_display = ('order', 'product', 'quantity', 'price')
    search_fields = ('order__user__username', 'product__name')
    ordering = ('-order',)

admin.site.register(OrderItem, OrderItemAdmin)

# ShippingDetails Admin
class ShippingDetailsAdmin(admin.ModelAdmin):
    list_display = ('order', 'address', 'city', 'postal_code')
    search_fields = ('order__user__username', 'address')
    ordering = ('-order',)

admin.site.register(ShippingDetails, ShippingDetailsAdmin)

# Payment Admin
class PaymentAdmin(admin.ModelAdmin):
    list_display = ('order', 'payment_method', 'amount', 'payment_status', 'created_at')
    search_fields = ('order__user__username',)
    list_filter = ('payment_method', 'payment_status')
    ordering = ('-created_at',)

admin.site.register(Payment, PaymentAdmin)

# Profile Admin
class ProfileAdmin(admin.ModelAdmin):
    list_display = ('user', 'phone_number')
    search_fields = ('user__username', 'phone_number')

admin.site.register(Profile, ProfileAdmin)
