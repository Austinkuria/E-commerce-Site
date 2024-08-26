from django.db import models
from django.contrib.auth.models import User
from django.core.validators import RegexValidator
from django.db.models.signals import post_save
from django.dispatch import receiver

# Product Model: Represents a product available in the store
class Product(models.Model):
    name = models.CharField(max_length=255)  # Name of the product
    price = models.DecimalField(max_digits=10, decimal_places=2)  # Price of the product
    image = models.ImageField(upload_to='products_images/', blank=True)  # Image of the product, not required
    description = models.TextField(blank=True, null=True)  # Description of the product, can be left blank
    rating = models.PositiveIntegerField(default=0)  # Rating of the product, default is 0
    reviews = models.PositiveIntegerField(default=0)  # Number of reviews, default is 0

    def __str__(self):
        return self.name  # Return the product name for display purposes

    def get_total_price(self, quantity):
        """Calculate the total price for the given quantity of the product."""
        return self.price * quantity

# Cart Model: Represents a user's shopping cart
class Cart(models.Model):
    user = models.OneToOneField(User, on_delete=models.CASCADE)  # One cart per user
    created_at = models.DateTimeField(auto_now_add=True)  # Timestamp when the cart was created

    def __str__(self):
        return f"Cart of {self.user.username}"  # Display a readable string representation of the cart

    def get_items(self):
        """Retrieve all items in the cart."""
        return CartItem.objects.filter(cart=self)

    def get_total_price(self):
        """Calculate the total price of all items in the cart."""
        return sum(item.get_total_price() for item in self.get_items())

# CartItem Model: Represents an item in a cart
class CartItem(models.Model):
    cart = models.ForeignKey(Cart, on_delete=models.CASCADE)  # Link to the cart this item belongs to
    product = models.ForeignKey(Product, on_delete=models.CASCADE)  # The product this item represents
    quantity = models.PositiveIntegerField(default=1)  # Quantity of the product

    def __str__(self):
        return f"{self.quantity} x {self.product.name} in {self.cart.user.username}'s cart"  # Display the item in a readable format

    def get_total_price(self):
        """Calculate the total price for this cart item based on its quantity."""
        return self.product.get_total_price(self.quantity)

    def increase_quantity(self, amount=1):
        """Increase the quantity of this cart item by the specified amount."""
        self.quantity += amount
        self.save()

    def decrease_quantity(self, amount=1):
        """Decrease the quantity of this cart item by the specified amount. Remove the item if quantity becomes zero or less."""
        if self.quantity - amount <= 0:
            self.delete()
        else:
            self.quantity -= amount
            self.save()

# Order Model: Represents a completed order by a user
class Order(models.Model):
    user = models.ForeignKey(User, on_delete=models.CASCADE)  # User who placed the order
    total = models.DecimalField(max_digits=10, decimal_places=2)  # Total amount for the order
    address = models.CharField(max_length=255)  # Delivery address
    city = models.CharField(max_length=100)  # City of delivery
    postal_code = models.CharField(max_length=20)  # Postal code for the delivery
    created_at = models.DateTimeField(auto_now_add=True)  # Timestamp when the order was created

    def __str__(self):
        return f"Order {self.id} by {self.user.username}"  # Display the order ID and user for clarity

    def calculate_total(self):
        """Calculate the total price for this order, including all items."""
        return sum(item.get_total_price() for item in self.items.all())

# OrderItem Model: Represents a product included in an order
class OrderItem(models.Model):
    order = models.ForeignKey(Order, related_name='items', on_delete=models.CASCADE)  # Link to the order this item belongs to
    product = models.ForeignKey(Product, on_delete=models.CASCADE)  # The product this item represents
    quantity = models.PositiveIntegerField()  # Quantity of the product ordered

    def get_total_price(self):
        """Calculate the total price for this order item based on its quantity."""
        return self.quantity * self.product.price

    def __str__(self):
        return f"{self.quantity} x {self.product.name}"  # Display the order item in a readable format

# Payment Model: Represents payment details for an order
class Payment(models.Model):
    PAYMENT_METHOD_CHOICES = [
        ('visa', 'Visa'),
        ('mastercard', 'MasterCard'),
        ('mpesa', 'M-Pesa'),
    ]

    order = models.OneToOneField(Order, on_delete=models.CASCADE)  # Link to the order this payment is for
    payment_method = models.CharField(max_length=20, choices=PAYMENT_METHOD_CHOICES)  # Payment method used
    amount = models.DecimalField(max_digits=10, decimal_places=2)  # Amount paid
    transaction_id = models.CharField(max_length=255, blank=True, null=True)  # Transaction ID, if available
    payment_status = models.CharField(max_length=20, default='pending')  # Status of the payment (default is 'pending')

    def __str__(self):
        return f"Payment for Order {self.order.id} via {self.get_payment_method_display()}"  # Display payment details

# ShippingDetails Model: Represents the shipping details for an order
class ShippingDetails(models.Model):
    user = models.OneToOneField(User, on_delete=models.CASCADE, null=True, blank=True)  # Link to the user, if applicable
    order = models.OneToOneField(Order, on_delete=models.CASCADE)  # Link to the order this shipping is for
    city = models.CharField(max_length=100)  # City of delivery
    address = models.CharField(max_length=255)  # Delivery address
    postal_code = models.CharField(max_length=20)  # Postal code for delivery

    def __str__(self):
        return f"{self.user.username}'s Shipping Details"  # Display shipping details for clarity

# Profile Model: Represents additional information about a user
class Profile(models.Model):
    user = models.OneToOneField(User, on_delete=models.CASCADE)  # Link to the user this profile belongs to
    phone_number = models.CharField(
        max_length=15,
        blank=True,
        null=True,
        validators=[RegexValidator(regex=r'^\+?1?\d{9,15}$', message="Phone number must be entered in the format: '+999999999'. Up to 15 digits allowed.")]
    )  # Phone number with validation, can be left blank
    address = models.CharField(max_length=255, blank=True, null=True)  # Address of the user, can be left blank
    city = models.CharField(max_length=100, blank=True, null=True)  # City of the user, can be left blank
    postal_code = models.CharField(max_length=20, blank=True, null=True)  # Postal code of the user, can be left blank
    profile_picture = models.ImageField(upload_to='profile_pictures/', default='default.jpg')  # Profile picture with a default image

    def __str__(self):
        return f'{self.user.username} Profile'  # Display profile information for clarity

    def save(self, *args, **kwargs):
        """Save the profile, ensuring it's correctly saved."""
        super().save(*args, **kwargs)

# Signal handlers to automatically create and save user profiles
@receiver(post_save, sender=User)
def create_user_profile(sender, instance, created, **kwargs):
    """Create a profile when a new user is created."""
    if created:
        Profile.objects.create(user=instance)

@receiver(post_save, sender=User)
def save_user_profile(sender, instance, **kwargs):
    """Save the profile when the user is saved."""
    instance.profile.save()
