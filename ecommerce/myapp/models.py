from django.db import models
from django.contrib.auth.models import User
from django.core.validators import RegexValidator, MinValueValidator
from django.db.models.signals import post_save
from django.dispatch import receiver

# Product Model: Represents a product available in the store
class Product(models.Model):
    name = models.CharField(max_length=255)  # The name of the product, with a maximum length of 255 characters
    price = models.DecimalField(
        max_digits=12, decimal_places=2, default=0, validators=[MinValueValidator(0)]
    )  # The price of the product, with up to 12 digits, including 2 decimal places; default is 0 and must be non-negative
    image = models.ImageField(upload_to='products_images/', blank=True)  # Optional image of the product; if provided, stored in 'products_images/' directory
    description = models.TextField(blank=True, null=True)  # Optional text description of the product; can be left blank or set to null
    rating = models.DecimalField(
        max_digits=4, decimal_places=2, default=0, validators=[MinValueValidator(0)]
    )  # The rating of the product, with up to 4 digits, including 2 decimal places; default is 0 and must be non-negative
    reviews = models.CharField(max_length=255)  # Product reviews, limited to 255 characters

    def __str__(self):
        return self.name  # Returns the product name when the object is printed or displayed

    def get_total_price(self, quantity):
        """Calculate the total price for the given quantity of the product."""
        return self.price * quantity  # Multiplies the product's price by the quantity to get the total price

# Cart Model: Represents a user's shopping cart
class Cart(models.Model):
    user = models.OneToOneField(User, on_delete=models.CASCADE)  # Each user has one cart; when a user is deleted, their cart is also deleted
    created_at = models.DateTimeField(auto_now_add=True)  # Automatically set the timestamp when the cart is created

    def __str__(self):
        return f"Cart of {self.user.username}"  # Returns a string representation of the cart, including the username of the owner

    def get_items(self):
        """Retrieve all items in the cart."""
        return CartItem.objects.filter(cart=self)  # Fetches all CartItem objects associated with this cart

    def get_total_price(self):
        """Calculate the total price of all items in the cart."""
        return sum(item.get_total_price() for item in self.get_items())  # Sums the total price of each item in the cart

# CartItem Model: Represents an item in a cart
class CartItem(models.Model):
    cart = models.ForeignKey(Cart, on_delete=models.CASCADE)  # Link to the cart this item belongs to; if the cart is deleted, this item is also deleted
    product = models.ForeignKey(Product, on_delete=models.CASCADE)  # The product this item represents; if the product is deleted, this item is also deleted
    quantity = models.PositiveIntegerField(default=1)  # The quantity of the product in the cart; default is 1

    def __str__(self):
        return f"{self.quantity} x {self.product.name} in {self.cart.user.username}'s cart"  # Returns a string representation of the cart item

    def get_total_price(self):
        """Calculate the total price for this cart item based on its quantity."""
        return self.product.get_total_price(self.quantity)  # Uses the Product's method to calculate the total price for this item

    def increase_quantity(self, amount=1):
        """Increase the quantity of this cart item by the specified amount."""
        self.quantity += amount  # Adds the specified amount to the current quantity
        self.save()  # Saves the updated quantity to the database

    def decrease_quantity(self, amount=1):
        """Decrease the quantity of this cart item by the specified amount. Remove the item if quantity becomes zero or less."""
        if self.quantity - amount <= 0:
            self.delete()  # Deletes the cart item if the quantity falls to zero or below
        else:
            self.quantity -= amount  # Reduces the quantity by the specified amount
            self.save()  # Saves the updated quantity to the database

# Order Model: Represents a completed order by a user
class Order(models.Model):
    user = models.ForeignKey(User, on_delete=models.CASCADE)  # Link to the user who placed the order; if the user is deleted, the order is also deleted
    total = models.DecimalField(max_digits=10, decimal_places=2)  # Total amount for the order; up to 10 digits with 2 decimal places
    address = models.CharField(max_length=255)  # Delivery address; limited to 255 characters
    city = models.CharField(max_length=100)  # City of delivery; limited to 100 characters
    postal_code = models.CharField(max_length=20)  # Postal code for the delivery; limited to 20 characters
    created_at = models.DateTimeField(auto_now_add=True)  # Automatically set the timestamp when the order is created
    shipping_fee = models.DecimalField(max_digits=10, decimal_places=2, default=0.00)  # Shipping fee; up to 10 digits with 2 decimal places; default is 0.00

    def __str__(self):
        return f"Order {self.id} by {self.user.username}"  # Returns a string representation of the order, including the order ID and username of the user

    def get_cart_items(self):
        """Retrieve all items associated with this order."""
        return sum(item.quantity for item in self.items.all())  # Sums the quantity of each item in the order

    def calculate_total(self):
        """Calculate the total price for this order, including all items."""
        return sum(item.get_total_price() for item in self.items.all())  # Sums the total price of each item in the order

# OrderItem Model: Represents a product included in an order
class OrderItem(models.Model):
    order = models.ForeignKey(Order, related_name='items', on_delete=models.CASCADE)  # Link to the order this item belongs to; if the order is deleted, this item is also deleted
    product = models.ForeignKey(Product, on_delete=models.CASCADE)  # The product this item represents; if the product is deleted, this item is also deleted
    quantity = models.PositiveIntegerField()  # Quantity of the product ordered
    price = models.DecimalField(
        max_digits=12,
        decimal_places=2,
        default=0,
        validators=[MinValueValidator(0)]
    )  # Price of the product in the order; up to 12 digits with 2 decimal places; default is 0 and must be non-negative

    @property
    def total_price(self):
        """Calculate the total price for this order item based on its quantity and product price."""
        return self.quantity * self.price  # Multiplies the quantity by the price to get the total price

    def __str__(self):
        return f"{self.quantity} x {self.product.name}"  # Returns a string representation of the order item

# Payment Model: Represents payment details for an order
class Payment(models.Model):
    PAYMENT_METHOD_CHOICES = [
        ('visa', 'Visa'),
        ('mastercard', 'MasterCard'),
        ('mpesa', 'M-Pesa'),
    ]  # Choices for payment methods

    order = models.OneToOneField(Order, on_delete=models.CASCADE)  # Link to the order this payment is for; if the order is deleted, this payment is also deleted
    payment_method = models.CharField(max_length=20, choices=PAYMENT_METHOD_CHOICES)  # Payment method used, limited to 20 characters
    amount = models.DecimalField(max_digits=10, decimal_places=2)  # Amount paid; up to 10 digits with 2 decimal places
    transaction_id = models.CharField(max_length=255, blank=True, null=True)  # Optional transaction ID; can be left blank or set to null
    payment_status = models.CharField(max_length=20, default='pending')  # Status of the payment; default is 'pending'

    def __str__(self):
        return f"Payment for Order {self.order.id} via {self.get_payment_method_display()}"  # Returns a string representation of the payment details

# ShippingDetails Model: Represents the shipping details for an order
class ShippingDetails(models.Model):
    user = models.OneToOneField(User, on_delete=models.CASCADE, null=True, blank=True)  # Optional link to the user; if the user is deleted, the shipping details are also deleted
    order = models.OneToOneField(Order, on_delete=models.CASCADE)  # Link to the order this shipping is for; if the order is deleted, this shipping detail is also deleted
    address = models.CharField(
        max_length=255,
        error_messages={
            'max_length': 'Address cannot be longer than 255 characters.'
        }
    )  # Delivery address; limited to 255 characters with a custom error message for exceeding the limit
    city = models.CharField(
        max_length=100,
        validators=[RegexValidator(
            regex=r'^[a-zA-Z\s]+$',
            message="City name must contain only letters and spaces."
        )],
        error_messages={
            'max_length': 'City name cannot be longer than 100 characters.'
        }
    )  # City of delivery; limited to 100 characters with validation to ensure only letters and spaces are allowed
    postal_code = models.CharField(
        max_length=20,
        validators=[RegexValidator(
            regex=r'^\d{4,10}$',
            message="Postal code must contain between 4 and 10 digits."
        )],
        error_messages={
            'max_length': 'Postal code cannot be longer than 20 characters.'
        }
    )  # Postal code for delivery; limited to 20 characters with validation for 4 to 10 digits

    def __str__(self):
        return f"{self.user.username}'s Shipping Details"  # Returns a string representation of the shipping details, including the username of the user

class Profile(models.Model):
    user = models.OneToOneField(User, on_delete=models.CASCADE)  # Link to the user; if the user is deleted, the profile is also deleted
    phone_number = models.CharField(
        max_length=15,
        blank=True,
        null=True,
        validators=[RegexValidator(
            regex=r'^\+?\d{10,15}$',
            message="Phone number must be in the format: '+1234567890'. Up to 15 digits allowed."
        )],
        error_messages={
            'max_length': 'Phone number cannot be longer than 15 characters.'
        }
    )  # Optional phone number; up to 15 characters with validation for format and length
    address = models.CharField(
        max_length=255,
        blank=True,
        null=True,
        error_messages={
            'max_length': 'Address cannot be longer than 255 characters.'
        }
    )  # Optional address; up to 255 characters with a custom error message for exceeding the limit
    city = models.CharField(
        max_length=100,
        blank=True,
        null=True,
        validators=[RegexValidator(
            regex=r'^[a-zA-Z\s]+$',
            message="City name must contain only letters and spaces."
        )],
        error_messages={
            'max_length': 'City name cannot be longer than 100 characters.'
        }
    )  # Optional city; up to 100 characters with validation for format and length
    postal_code = models.CharField(
        max_length=20,
        blank=True,
        null=True,
        validators=[RegexValidator(
            regex=r'^\d{4,10}$',
            message="Postal code must contain between 4 and 10 digits."
        )],
        error_messages={
            'max_length': 'Postal code cannot be longer than 20 characters.'
        }
    )  # Optional postal code; up to 20 characters with validation for format and length
    profile_picture = models.ImageField(
        upload_to='profile_pictures/',
        default='default.jpg'
    )  # Optional profile picture; uploaded to 'profile_pictures/' directory with a default image

    def __str__(self):
        return f'{self.user.username} Profile'  # Returns a string representation of the profile, including the username of the user

    def save(self, *args, **kwargs):
        super().save(*args, **kwargs)  # Calls the parent class's save method to save the profile

@receiver(post_save, sender=User)
def create_user_profile(sender, instance, created, **kwargs):
    """Create a Profile instance whenever a new User instance is created."""
    if created:
        Profile.objects.create(user=instance)  # Creates a new Profile for the newly created User

@receiver(post_save, sender=User)
def save_user_profile(sender, instance, **kwargs):
    """Save the Profile instance whenever the User instance is saved."""
    instance.profile.save()  # Saves the associated Profile whenever the User is saved

class SalesReport(models.Model):
    product = models.ForeignKey('Product', on_delete=models.CASCADE)  # Link to the product this report is for; if the product is deleted, this report is also deleted
    quantity_sold = models.IntegerField()  # Quantity of the product sold
    total_revenue = models.DecimalField(max_digits=10, decimal_places=2)  # Total revenue from the sales; up to 10 digits with 2 decimal places
    report_date = models.DateField()  # Date of the sales report

    def __str__(self):
        return f"Sales Report for {self.product.name} on {self.report_date}"  # Returns a string representation of the sales report, including product name and report date
