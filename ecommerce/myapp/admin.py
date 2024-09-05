from django import views
from django.contrib import admin
from .models import Product, Cart, CartItem, Order, OrderItem, ShippingDetails, Profile, SalesReport
from django.utils.translation import gettext_lazy as _
from django.contrib.admin import AdminSite
from django.urls import path

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

class CustomAdminSite(AdminSite):
    site_header = _('My E-commerce Admin')
    site_title = _('E-commerce Admin')

    def get_urls(self):
        urls = super().get_urls()
        urls += [
                    path('', views.CustomDashboardView.as_view(), name='custom_dashboard'),
                    # CRUD operations for all models
                    # Product
                    path('products/add/', views.ProductCreateView.as_view(), name='product_create'),
                    path('products/<int:pk>/update/', views.ProductUpdateView.as_view(), name='product_update'),
                    path('products/<int:pk>/delete/', views.ProductDeleteView.as_view(), name='product_delete'),

                    # Cart
                    path('carts/add/', views.CartCreateView.as_view(), name='cart_create'),
                    path('carts/<int:pk>/update/', views.CartUpdateView.as_view(), name='cart_update'),
                    path('carts/<int:pk>/delete/', views.CartDeleteView.as_view(), name='cart_delete'),
                    # CartItem
                    path('cartitems/add/', views.CartItemCreateView.as_view(), name='cartitem_create'),
                    path('cartitems/<int:pk>/update/', views.CartItemUpdateView.as_view(), name='cartitem_update'),
                    path('cartitems/<int:pk>/delete/', views.CartItemDeleteView.as_view(), name='cartitem_delete'),
                    # Order
                    path('orders/add/', views.OrderCreateView.as_view(), name='order_create'),
                    path('orders/<int:pk>/update/', views.OrderUpdateView.as_view(), name='order_update'),

                    path('orders/<int:pk>/delete/', views.OrderDeleteView.as_view(), name='order_delete'), 

                    # OrderItem
                    path('orderitems/add/', views.OrderItemCreateView.as_view(), name='orderitem_create'),
                    path('orderitems/<int:pk>/update/', views.OrderItemUpdateView.as_view(), name='orderitem_update'),
                    path('orderitems/<int:pk>/delete/', views.OrderItemDeleteView.as_view(), name='orderitem_delete'),
                    # ShippingDetails
                    path('shippingdetails/add/', views.ShippingDetailsCreateView.as_view(), name='shippingdetails_create'),
                    path('shippingdetails/<int:pk>/update/', views.ShippingDetailsUpdateView.as_view(), name='shippingdetails_update'),
                    path('shippingdetails/<int:pk>/delete/', views.ShippingDetailsDeleteView.as_view(), name='shippingdetails_delete'),
                    # Profile
                    path('profiles/add/', views.ProfileCreateView.as_view(), name='profile_create'),
                    path('profiles/<int:pk>/update/', views.ProfileUpdateView.as_view(), name='profile_update'),
                    path('profiles/<int:pk>/delete/', views.ProfileDeleteView.as_view(), name='profile_delete'),

                    # SalesReport
                    path('salesreports/add/', views.SalesReportCreateView.as_view(), name='salesreport_create'),
                    path('salesreports/<int:pk>/update/', views.SalesReportUpdateView.as_view(), name='salesreport_update'),
                    path('salesreports/<int:pk>/delete/', views.SalesReportDeleteView.as_view(), name='salesreport_delete'),
                ]
        return urls
