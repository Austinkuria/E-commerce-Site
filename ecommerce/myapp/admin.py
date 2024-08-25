from django.contrib import admin
from .models import Product, Cart, CartItem, Order, OrderItem, ShippingDetails, Profile

from django.contrib import admin
class ProductAdmin(admin.ModelAdmin):
    list_display = ('name', 'price', 'image_tag', 'rating')  # Display these fields in the list view
    search_fields = ('name',)  # Add a search bar for the 'name' field
    list_filter = ('price', 'rating')  # Add a filter sidebar by 'price' and 'rating'
    ordering = ('-price',)  # Optional: Order products by price, descending

    # Optionally, configure how the form is displayed on the admin page
    fields = ('name', 'price', 'description', 'rating', 'reviews', 'image')  # Order fields as they appear in the admin form

    # Optionally, customize how the image field is displayed in the admin list view
    def image_tag(self, obj):
        if obj.image:
            return '<img src="%s" width="100" height="100" />' % obj.image.url
        return 'No image'
    image_tag.allow_tags = True
    image_tag.short_description = 'Image'

admin.site.register(Product, ProductAdmin)
# admin.site.register(ShippingDetails)
@admin.register(Cart)
class CartAdmin(admin.ModelAdmin):
    list_display = ('user', 'created_at')
    search_fields = ('user__username',)

@admin.register(CartItem)
class CartItemAdmin(admin.ModelAdmin):
    list_display = ('cart', 'product', 'quantity')
    search_fields = ('cart__user__username', 'product__name')

@admin.register(Order)
class OrderAdmin(admin.ModelAdmin):
    list_display = ('user', 'total', 'created_at')
    search_fields = ('user__username',)

@admin.register(OrderItem)
class OrderItemAdmin(admin.ModelAdmin):
    list_display = ('order', 'product', 'quantity')
    search_fields = ('order__user__username', 'product__name')
# ShippingDetails Admin
class ShippingDetailsAdmin(admin.ModelAdmin):
    list_display = ('order', 'address', 'city', 'postal_code')
    search_fields = ('order__user__username', 'address')
    ordering = ('-order',)

admin.site.register(ShippingDetails, ShippingDetailsAdmin)

# Profile Admin
class ProfileAdmin(admin.ModelAdmin):
    list_display = ('user', 'phone_number')
    search_fields = ('user__username', 'phone_number')

admin.site.register(Profile, ProfileAdmin)
