from django.shortcuts import render, get_object_or_404, redirect
from django.http import JsonResponse, HttpResponseBadRequest
from django.contrib import messages
from django.contrib.auth import authenticate, login
from django.contrib.auth.decorators import login_required
from django.views.decorators.csrf import csrf_protect, csrf_exempt
from django.contrib.auth.views import LogoutView
from django.urls import reverse
from .models import Product, Cart, CartItem, Order, OrderItem, Profile, Payment, ShippingDetails
from .forms import CustomUserCreationForm, CustomLoginForm, UserUpdateForm, ProfileUpdateForm, CheckoutForm
import logging
from django.middleware.csrf import get_token

logger = logging.getLogger(__name__)

# View to list all products on the home page
def products_view(request):
    products = Product.objects.all()  # Retrieve all products from the database
    return render(request, 'index.html', {'products': products})  # Render the product list on the home page

# View to get the current user's cart items
@login_required
def get_cart(request):
    cart = get_object_or_404(Cart, user=request.user)  # Retrieve the user's cart or return a 404 if not found
    cart_items = CartItem.objects.filter(cart=cart)  # Get all items in the cart
    
    # Prepare data for the JSON response
    cart_items_data = [
        {
            'id': item.product.id,
            'name': item.product.name,
            'price': item.product.price,
            'quantity': item.quantity
        }
        for item in cart_items
    ]
    
    return JsonResponse({'cart_items': cart_items_data})  # Return cart items as a JSON response

# View to handle adding a product to the cart
@csrf_exempt
def add_to_cart(request):
    if request.method == 'POST':
        product_id = int(request.POST.get('product_id'))  # Extract product ID from the POST request
        quantity = int(request.POST.get('quantity'))  # Extract quantity from the POST request
        product = get_object_or_404(Product, id=product_id)  # Retrieve the product or return a 404 if not found

        # Retrieve or create a cart for the user
        cart, created = Cart.objects.get_or_create(user=request.user)
        
        # Retrieve or create a cart item for this product in the user's cart
        cart_item, created = CartItem.objects.get_or_create(cart=cart, product=product)
        if not created:
            cart_item.increase_quantity(quantity)  # Update quantity if item already exists
        else:
            cart_item.quantity = quantity  # Set initial quantity if item is new
            cart_item.save()
        
        return JsonResponse({'status': 'success'})  # Return success response
    
    return JsonResponse({'status': 'error'}, status=400)  # Return error response for non-POST requests


# View to handle removing a product from the cart
@csrf_exempt
def remove_from_cart(request):
    if request.method == 'POST':
        product_id = int(request.POST.get('product_id'))  # Extract product ID from POST request
        cart = get_object_or_404(Cart, user=request.user)  # Retrieve the user's cart or return a 404
        product = get_object_or_404(Product, id=product_id)  # Retrieve the product or return a 404
        
        try:
            cart_item = CartItem.objects.get(cart=cart, product=product)  # Get the specific cart item
            cart_item.delete()  # Remove the item from the cart
            return JsonResponse({'status': 'success'})  # Return success response
        except CartItem.DoesNotExist:
            return JsonResponse({'status': 'error', 'message': 'Item not found in cart'}, status=404)  # Return error if item not found
    
    return JsonResponse({'status': 'error'}, status=400)  # Return error for non-POST requests

# View to update the quantity of a product in the cart
@csrf_exempt
def update_cart(request):
    if request.method == 'POST':
        product_id = int(request.POST.get('product_id'))  # Extract product ID from POST request
        action = request.POST.get('action')  # Extract action ('increase' or 'decrease')
        cart = get_object_or_404(Cart, user=request.user)  # Retrieve the user's cart or return a 404
        product = get_object_or_404(Product, id=product_id)  # Retrieve the product or return a 404
        cart_item, created = CartItem.objects.get_or_create(cart=cart, product=product)  # Retrieve or create cart item
        
        if action == 'increase':
            cart_item.increase_quantity()  # Increase quantity if action is 'increase'
        elif action == 'decrease':
            cart_item.decrease_quantity()  # Decrease quantity if action is 'decrease'
        
        if cart_item.quantity <= 0:
            cart_item.delete()  # Remove item if quantity drops to 0 or below
        
        return JsonResponse({'status': 'success'})  # Return success response
    
    return JsonResponse({'status': 'error'}, status=400)  # Return error for non-POST requests

# View to provide the CSRF token for JavaScript to use
def csrf_token(request):
    return JsonResponse({'csrfToken': get_token(request)})  # Return CSRF token in JSON response

# View to display and update user profile
@login_required
@csrf_protect
def profile(request):
    if not hasattr(request.user, 'profile'):
        Profile.objects.create(user=request.user)  # Create profile if it doesn't exist

    if request.method == 'POST':
        user_form = UserUpdateForm(request.POST, instance=request.user)  # Form for updating user details
        profile_form = ProfileUpdateForm(request.POST, request.FILES, instance=request.user.profile)  # Form for updating profile details
        if user_form.is_valid() and profile_form.is_valid():
            user_form.save()  # Save user details
            profile_form.save()  # Save profile details
            messages.success(request, 'Your profile has been updated!')  # Success message
            return redirect('profile')  # Redirect to profile page
        else:
            messages.error(request, 'Please correct the errors below.')  # Error message if forms are invalid
    else:
        user_form = UserUpdateForm(instance=request.user)  # Prepopulate form with current user data
        profile_form = ProfileUpdateForm(instance=request.user.profile)  # Prepopulate form with current profile data

    return render(request, 'users/profile.html', {'user_form': user_form, 'profile_form': profile_form})  # Render profile page

# View to handle user registration
@csrf_protect
def signup_view(request):
    if request.method == 'POST':
        form = CustomUserCreationForm(request.POST)  # Form for user registration
        if form.is_valid():
            user = form.save()  # Save new user
            login(request, user)  # Log in the newly registered user
            next_page = request.session.get('next_page', 'index')  # Get next page to redirect to
            return redirect(next_page)  # Redirect to the next page
        else:
            messages.error(request, 'Please correct the errors below.')  # Error message if form is invalid
    else:
        form = CustomUserCreationForm()  # Empty form for GET request

    return render(request, 'user_auth/signup.html', {'form': form})  # Render registration page

# View to handle user login
@csrf_protect
def login_view(request):
    if request.method == 'POST':
        form = CustomLoginForm(request, data=request.POST)  # Form for user login
        if form.is_valid():
            username = form.cleaned_data.get('username')
            password = form.cleaned_data.get('password')
            user = authenticate(username=username, password=password)  # Authenticate user
            if user is not None:
                login(request, user)  # Log in the user
                if user.is_superuser:
                    return redirect(reverse('admin:index'))  # Redirect superusers to the admin dashboard
                next_page = request.session.get('next_page', 'index')  # Get next page to redirect to
                request.session.pop('next_page', None)  # Clear next_page from session
                return redirect(next_page)  # Redirect to the next page
        else:
            messages.error(request, 'Please correct the errors below.')  # Error message if form is invalid
    else:
        form = CustomLoginForm()  # Empty form for GET request

    return render(request, 'registration/login.html', {'form': form})  # Render login page

# View to redirect authenticated users to checkout or login for unauthenticated users
@csrf_protect
def some_view(request):
    profiles = Profile.objects.filter(user__is_superuser=False)  # Filter out admin profiles

    if request.user.is_authenticated:
        return redirect('checkout')  # Redirect authenticated users to checkout page
    else:
        request.session['next_page'] = request.path  # Save current path to session
        return redirect('login')  # Redirect unauthenticated users to login page

# Custom logout view that provides a message on successful logout
class CustomLogoutView(LogoutView):
    def get(self, request, *args, **kwargs):
        messages.info(request, "You have been logged out successfully.")  # Log out message
        return super().get(request, *args, **kwargs)  # Proceed with default logout behavior

# View to check if a user is logged in
def is_logged_in(request):
    return JsonResponse({'is_authenticated': request.user.is_authenticated})  # Return authentication status as JSON

# Function to calculate shipping fee based on total price
def calculate_shipping_fee(total_price):
    if total_price is None:
        return 0  # Return default fee if no price is provided

    if total_price <= 1000:
        return 50  # Return shipping fee for orders up to 1000
    elif total_price <= 5000:
        return 100  # Return shipping fee for orders between 1001 and 5000
    else:
        return 150  # Return shipping fee for orders above 5000

# View to handle checkout process
@login_required
@csrf_protect
def checkout_view(request):
    try:
        cart = Cart.objects.get(user=request.user)  # Retrieve the user's cart
    except Cart.DoesNotExist:
        cart = Cart.objects.create(user=request.user)  # Create a new cart if it doesn't exist

    cart_items = CartItem.objects.filter(cart=cart)  # Get all items in the cart

    if request.method == 'POST':
        form = CheckoutForm(request.POST)  # Form for checkout details
        payment_method = request.POST.get('payment_method')  # Extract payment method from POST request

        if form.is_valid():
            total_price = cart.get_total_price()  # Calculate total price of items in the cart
            shipping_fee = calculate_shipping_fee(total_price)  # Calculate shipping fee
            
            # Create and save the order
            order = Order.objects.create(
                user=request.user,
                total=total_price + shipping_fee,
                address=form.cleaned_data['address'],
                city=form.cleaned_data['city'],
                postal_code=form.cleaned_data['postal_code']
            )
            
            order.shipping_fee = shipping_fee
            order.save()

            # Create order items for each cart item
            for item in cart_items:
                OrderItem.objects.create(order=order, product=item.product, quantity=item.quantity)

            # Create and save shipping details
            ShippingDetails.objects.create(
                user=request.user,
                order=order,
                address=form.cleaned_data['address'],
                city=form.cleaned_data['city'],
                postal_code=form.cleaned_data['postal_code']
            )

            # Create and save payment details
            Payment.objects.create(
                order=order,
                payment_method=payment_method,
                amount=order.total,
                transaction_id="N/A",
                payment_status="pending"
            )

            # Clear cart items after order is placed
            cart_items.delete()

            return redirect('order_confirmation', order_id=order.id)  # Redirect to order confirmation page
    else:
        form = CheckoutForm()  # Empty form for GET request

    # Calculate total price and shipping fee for display
    total_price = cart.get_total_price()  # Calculate total price
    shipping_fee = calculate_shipping_fee(total_price)  # Calculate shipping fee

    context = {
        'form': form,
        'cart_items': cart_items,
        'shipping_fee': shipping_fee,
        'total_price': total_price + shipping_fee,
    }
    return render(request, 'checkout.html', context)  # Render checkout page with context

# View to place an order and handle order creation
@login_required
@csrf_protect
def place_order(request):
    if request.method == 'POST':
        cart = Cart.objects.get(user=request.user)  # Retrieve the user's cart
        cart_items = CartItem.objects.filter(cart=cart)  # Get all items in the cart

        if not cart_items.exists():
            return JsonResponse({'status': 'error', 'message': 'Your cart is empty.'}, status=400)  # Error if cart is empty

        try:
            # Calculate total price and shipping fee
            total_price = sum(item.product.price * item.quantity for item in cart_items)
            shipping_fee = calculate_shipping_fee(total_price)
            
            # Create and save the order
            order = Order.objects.create(user=request.user)
            for item in cart_items:
                OrderItem.objects.create(order=order, product=item.product, quantity=item.quantity, price=item.product.price)
            
            order.shipping_fee = shipping_fee
            order.total_price = total_price + shipping_fee
            order.save()

            # Clear cart items after order is placed
            cart_items.delete()

            return redirect('order_confirmation', order_id=order.id)  # Redirect to order confirmation page
        except Exception as e:
            logger.error(f"Error placing order: {e}")  # Log error if placing order fails
            return JsonResponse({'status': 'error', 'message': 'An error occurred while placing your order.'}, status=500)  # Return error response
    else:
        return HttpResponseBadRequest("Invalid request method.")  # Return error for non-POST requests

# View to display order confirmation
@login_required
def order_confirmation_view(request, order_id):
    try:
        order = Order.objects.get(id=order_id, user=request.user)  # Retrieve the order or return a 404 if not found
    except Order.DoesNotExist:
        return redirect('checkout')  # Redirect to checkout if order does not exist

    # Calculate total price and shipping fee for the order
    total_price = sum(item.get_total_price() for item in order.items.all())
    shipping_fee = calculate_shipping_fee(total_price)

    context = {
        'order': order,
        'order_items': order.items.all(),
        'total_price': total_price,
        'shipping_fee': shipping_fee,
    }
    return render(request, 'order_confirmation.html', context)  # Render order confirmation page with context
