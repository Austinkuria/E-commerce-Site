from django.contrib import admin
from .models import Product
from .models import ShippingDetails
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
admin.site.register(ShippingDetails)