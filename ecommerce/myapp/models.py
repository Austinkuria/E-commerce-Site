from django.db import models
from django.contrib.auth.models import User
from django.core.validators import RegexValidator
from django.db import transaction

# Product Model
class Product(models.Model):
    name = models.CharField(max_length=255)
    price = models.DecimalField(max_digits=10, decimal_places=2)
    image = models.ImageField(upload_to='products_images/', blank=True, null=True)
    description = models.TextField(blank=True, null=True)
    rating = models.PositiveIntegerField(default=0)
    reviews = models.PositiveIntegerField(default=0)
    stock = models.PositiveIntegerField(default=0)  # Manage inventory

    def __str__(self):
        return self.name

    def is_in_stock(self):
        return self.stock > 0

    @transaction.atomic
    def reduce_stock(self, quantity):
        if self.stock >= quantity:
            self.stock -= quantity
            self.save()
        else:
            raise ValueError("Not enough stock available")

    @transaction.atomic
    def increase_stock(self, quantity):
        self.stock += quantity
        self.save()


# Cart Model
class Cart(models.Model):
    user = models.OneToOneField(User, on_delete=models.CASCADE)
    created_at = models.DateTimeField(auto_now_add=True)

    def __str__(self):
        return f"Cart of {self.user.username}"

    def get_total(self):
        cart_items = self.cartitem_set.all()
        total = sum(item.get_total_price() for item in cart_items)
        return total

    @transaction.atomic
    def add_item(self, product, quantity):
        if not product.is_in_stock():
            raise ValueError("Product is out of stock")

        # Use update_or_create to handle concurrent access
        cart_item, created = CartItem.objects.update_or_create(
            cart=self,
            product=product,
            defaults={'quantity': quantity}
        )
        if not created:
            cart_item.quantity += quantity
            cart_item.save()

        # Reduce stock for the product within the same transaction
        try:
            product.reduce_stock(quantity)
        except ValueError as e:
            # Rollback if stock cannot be reduced
            transaction.set_rollback(True)
            raise ValueError(str(e))

    @transaction.atomic
    def remove_item(self, product):
        cart_item = CartItem.objects.filter(cart=self, product=product).first()
        if cart_item:
            # Increase stock for the product
            product.increase_stock(cart_item.quantity)
            cart_item.delete()

    @transaction.atomic
    def clear(self):
        for cart_item in self.cartitem_set.all():
            # Increase stock for all items before clearing
            product.increase_stock(cart_item.quantity)
        self.cartitem_set.all().delete()


# CartItem Model
class CartItem(models.Model):
    cart = models.ForeignKey(Cart, on_delete=models.CASCADE)
    product = models.ForeignKey(Product, on_delete=models.CASCADE)
    quantity = models.PositiveIntegerField(default=1)

    def __str__(self):
        return f"{self.quantity} x {self.product.name} in {self.cart.user.username}'s cart"

    def get_total_price(self):
        return self.product.price * self.quantity


# Order Model
class Order(models.Model):
    STATUS_CHOICES = (
        ('pending', 'Pending'),
        ('completed', 'Completed'),
        ('shipped', 'Shipped'),
    )

    user = models.ForeignKey(User, on_delete=models.CASCADE)
    total_price = models.DecimalField(max_digits=10, decimal_places=2)
    shipping_fee = models.DecimalField(max_digits=10, decimal_places=2, default=0)
    status = models.CharField(max_length=20, choices=STATUS_CHOICES, default='pending')
    created_at = models.DateTimeField(auto_now_add=True)

    def __str__(self):
        return f"Order {self.id} by {self.user.username}"

    def calculate_total_price(self):
        items_total = sum(item.get_total_price() for item in self.items.all())
        return items_total + self.shipping_fee

    def save(self, *args, **kwargs):
        # Automatically calculate total price before saving
        self.total_price = self.calculate_total_price()
        super().save(*args, **kwargs)


# OrderItem Model
class OrderItem(models.Model):
    order = models.ForeignKey(Order, related_name='items', on_delete=models.CASCADE)
    product = models.ForeignKey(Product, on_delete=models.CASCADE)
    quantity = models.PositiveIntegerField()
    price = models.DecimalField(max_digits=10, decimal_places=2)

    def __str__(self):
        return f"{self.quantity} x {self.product.name} for Order {self.order.id}"

    def get_total_price(self):
        return self.price * self.quantity


# ShippingDetails Model
class ShippingDetails(models.Model):
    order = models.OneToOneField(Order, on_delete=models.CASCADE)
    address = models.CharField(max_length=255)
    city = models.CharField(max_length=100)
    postal_code = models.CharField(max_length=20)

    def __str__(self):
        return f"Shipping Details for Order {self.order.id}"


# Payment Model
class Payment(models.Model):
    PAYMENT_CHOICES = (
        ('visa', 'Visa Card'),
        ('mpesa', 'M-Pesa'),
        ('paypal', 'PayPal'),
    )

    order = models.ForeignKey(Order, on_delete=models.CASCADE)
    payment_method = models.CharField(max_length=20, choices=PAYMENT_CHOICES)
    amount = models.DecimalField(max_digits=10, decimal_places=2)
    transaction_id = models.CharField(max_length=100, blank=True, null=True)
    payment_status = models.CharField(max_length=20, default='pending')
    created_at = models.DateTimeField(auto_now_add=True)

    def __str__(self):
        return f"Payment {self.id} for Order {self.order.id}"


# Profile Model
class Profile(models.Model):
    user = models.OneToOneField(User, on_delete=models.CASCADE)
    phone_number = models.CharField(max_length=15, blank=True, null=True)
    address = models.CharField(max_length=255, blank=True, null=True)
    city = models.CharField(max_length=100, blank=True, null=True)
    postal_code = models.CharField(max_length=20, blank=True, null=True)
    profile_picture = models.ImageField(upload_to='profile_pictures/', default='default.jpg')

    def __str__(self):
        return f'{self.user.username} Profile'

    def save(self, *args, **kwargs):
        super().save(*args, **kwargs)