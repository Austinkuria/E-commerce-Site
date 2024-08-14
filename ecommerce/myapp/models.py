from django.db import models
from django.contrib.auth.models import User

# Create your models here.

class Product(models.Model):
    name = models.CharField(max_length=255)
    price = models.DecimalField(max_digits=10, decimal_places=2)
    image = models.ImageField(upload_to='index/')
    description = models.TextField(blank=True, null=True)  # Optional: Provide a description
    rating = models.PositiveIntegerField(default=0)  # Optional: Product rating (e.g., 1-5)
    reviews = models.PositiveIntegerField(default=0)  # Optional: Number of reviews

    def __str__(self):
        return self.name

class Cart(models.Model):
    user = models.OneToOneField(User, on_delete=models.CASCADE)
    created_at = models.DateTimeField(auto_now_add=True)
    # Optionally, add a total_price field
    total_price = models.DecimalField(max_digits=10, decimal_places=2, default=0.00, editable=False)

    def __str__(self):
        return f'Cart of {self.user.username}'

    def update_total_price(self):
        self.total_price = sum(item.total_price for item in self.items.all())
        self.save()

class CartItem(models.Model):
    cart = models.ForeignKey(Cart, related_name='items', on_delete=models.CASCADE)
    product = models.ForeignKey(Product, on_delete=models.CASCADE)
    quantity = models.PositiveIntegerField(default=1)
    # Optionally, add a total_price field for the cart item
    total_price = models.DecimalField(max_digits=10, decimal_places=2, editable=False, default=0.00)

    def save(self, *args, **kwargs):
        self.total_price = self.quantity * self.product.price
        super().save(*args, **kwargs)
        # Update the cart's total price when an item is saved
        self.cart.update_total_price()

    def __str__(self):
        return f'{self.quantity} x {self.product.name} in cart of {self.cart.user.username}'
