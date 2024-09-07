from django.contrib import admin
from .models import Product, Cart, CartItem, Order, OrderItem, ShippingDetails, Profile, SalesReport

# Admin configuration for the Product model
class ProductAdmin(admin.ModelAdmin):
    list_display = ('name', 'price', 'image_tag', 'rating')  # Fields to display in the list view of products
    search_fields = ('name',)  # Allows searching for products by their name
    list_filter = ('price', 'rating')  # Adds filters for products by price and rating
    ordering = ('-price',)  # Default ordering of products by price in descending order

    def image_tag(self, obj):
        """
        Custom method to display the product image as an HTML image tag in the admin list view.
        """
        if obj.image:
            return f'<img src="{obj.image.url}" width="100" height="100" />'  # Shows the product image with a fixed size
        return 'No image'  # Text shown if the product has no image
    image_tag.allow_tags = True  # Allows HTML tags in the admin interface
    image_tag.short_description = 'Image'  # Label for the image field in the list view

# Admin configuration for the Cart model
class CartAdmin(admin.ModelAdmin):
    list_display = ('user', 'created_at')  # Fields to display: user and creation date of the cart
    search_fields = ('user__username',)  # Allows searching for carts by the username of the user who owns the cart

# Admin configuration for the CartItem model
class CartItemAdmin(admin.ModelAdmin):
    list_display = ('cart', 'product', 'quantity')  # Fields to display: cart, product, and quantity of the item
    search_fields = ('cart__user__username', 'product__name')  # Allows searching for cart items by the username of the cart owner and product name

# Admin configuration for the Order model
class OrderAdmin(admin.ModelAdmin):
    list_display = ('user', 'total', 'created_at')  # Fields to display: user, total amount of the order, and creation date
    search_fields = ('user__username',)  # Allows searching for orders by the username of the user who placed the order

# Admin configuration for the OrderItem model
class OrderItemAdmin(admin.ModelAdmin):
    list_display = ('order', 'product', 'quantity')  # Fields to display: order, product, and quantity of the item
    search_fields = ('order__user__username', 'product__name')  # Allows searching for order items by the username of the order's owner and product name

# Admin configuration for the ShippingDetails model
class ShippingDetailsAdmin(admin.ModelAdmin):
    list_display = ('order', 'address', 'city', 'postal_code')  # Fields to display: order, address, city, and postal code
    search_fields = ('order__user__username', 'address')  # Allows searching for shipping details by the username of the order's owner and address
    ordering = ('-order',)  # Default ordering by the order field in descending order

# Admin configuration for the Profile model
class ProfileAdmin(admin.ModelAdmin):
    list_display = ('user', 'phone_number', 'address', 'city', 'postal_code')  # Fields to display: user, phone number, address, city, and postal code
    search_fields = ('user__username', 'phone_number')  # Allows searching for profiles by username and phone number

# Admin configuration for the SalesReport model
class SalesReportAdmin(admin.ModelAdmin):
    list_display = ('product', 'quantity_sold', 'total_revenue', 'report_date')  # Fields to display: product, quantity sold, total revenue, and report date
    list_filter = ('report_date', 'product')  # Adds filters for sales reports by date and product
    search_fields = ('product__name',)  # Allows searching for sales reports by product name

# Register the admin configurations with the admin site
admin.site.register(Product, ProductAdmin)  # Registers Product model with ProductAdmin configuration
admin.site.register(Cart, CartAdmin)  # Registers Cart model with CartAdmin configuration
admin.site.register(CartItem, CartItemAdmin)  # Registers CartItem model with CartItemAdmin configuration
admin.site.register(Order, OrderAdmin)  # Registers Order model with OrderAdmin configuration
admin.site.register(OrderItem, OrderItemAdmin)  # Registers OrderItem model with OrderItemAdmin configuration
admin.site.register(ShippingDetails, ShippingDetailsAdmin)  # Registers ShippingDetails model with ShippingDetailsAdmin configuration
admin.site.register(Profile, ProfileAdmin)  # Registers Profile model with ProfileAdmin configuration
admin.site.register(SalesReport, SalesReportAdmin)  # Registers SalesReport model with SalesReportAdmin configuration
