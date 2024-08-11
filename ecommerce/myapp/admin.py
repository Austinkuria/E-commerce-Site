from django.contrib import admin
from .models import Products

# Register your models here.
class ProductsAdmin(admin.ModelAdmin):
    list_display =('name','price','description','image')
    search_fields =('name','description')

admin.site.register(Products,ProductsAdmin)