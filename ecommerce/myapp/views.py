from django.shortcuts import render, get_object_or_404, redirect
from django.http import JsonResponse, HttpResponseBadRequest, HttpResponseForbidden
from django.contrib import messages
from django.contrib.auth import authenticate, login, logout
from django.contrib.auth.decorators import login_required
from django.views.decorators.csrf import csrf_protect, csrf_exempt
from django.urls import reverse  # To get the URL for admin:index
from .models import Product, Cart, CartItem, Order, OrderItem, Profile
from .forms import CustomUserCreationForm, CustomLoginForm, UserUpdateForm, ProfileUpdateForm, CheckoutForm
import logging
import json
from django.middleware.csrf import get_token
logger = logging.getLogger(__name__)

# Products View
def products_view(request):
    products = Product.objects.all()
    return render(request, 'index.html', {'products': products})
@login_required
def get_cart(request):
    # Retrieve the user's cart
    cart = get_object_or_404(Cart, user=request.user)
    
    # Retrieve all items in the cart
    cart_items = CartItem.objects.filter(cart=cart)
    
    # Prepare cart items data for JSON response
    cart_items_data = [
        {
            'id': item.product.id,
            'name': item.product.name,
            'price': item.product.price,
            'quantity': item.quantity
        }
        for item in cart_items
    ]
    
    return JsonResponse({'cart_items': cart_items_data})

@csrf_exempt
def add_to_cart(request):
    if request.method == 'POST':
        product_id = int(request.POST.get('product_id'))
        quantity = int(request.POST.get('quantity')) 
        product = get_object_or_404(Product, id=product_id)
    
        # Retrieve or create the user's cart
        cart, created = Cart.objects.get_or_create(user=request.user)
        
        # Retrieve or create a CartItem for this product in the user's cart
        cart_item, created = CartItem.objects.get_or_create(cart=cart, product=product)
        if not created:
            # If the item was already in the cart, update the quantity
            cart_item.increase_quantity(quantity)
        else:
            # If the item was just created, set the initial quantity
            cart_item.quantity = quantity
            cart_item.save()
        
        return JsonResponse({'status': 'success'})
    
    return JsonResponse({'status': 'error'}, status=400)


@csrf_exempt
def remove_from_cart(request):
    if request.method == 'POST':
        product_id = int(request.POST.get('product_id'))
        cart = get_object_or_404(Cart, user=request.user)  # Get the cart for the current user
        product = get_object_or_404(Product, id=product_id)
        
        # Get the cart item related to the product
        try:
            cart_item = CartItem.objects.get(cart=cart, product=product)
            cart_item.delete()  # Remove the item from the cart
            return JsonResponse({'status': 'success'})
        except CartItem.DoesNotExist:
            return JsonResponse({'status': 'error', 'message': 'Item not found in cart'}, status=404)
    
    return JsonResponse({'status': 'error'}, status=400)
@csrf_exempt
def update_cart(request):
    if request.method == 'POST':
        product_id = int(request.POST.get('product_id'))
        action = request.POST.get('action')

        # Get the user's cart
        cart = get_object_or_404(Cart, user=request.user)
        product = get_object_or_404(Product, id=product_id)
        
        # Get the cart item or create a new one if it doesn't exist
        cart_item, created = CartItem.objects.get_or_create(cart=cart, product=product)
        
        if action == 'increase':
            cart_item.increase_quantity()
        elif action == 'decrease':
            cart_item.decrease_quantity()
        
        # Optionally, check if the item quantity is 0 after decrease and remove it if necessary
        if cart_item.quantity <= 0:
            cart_item.delete()
        
        return JsonResponse({'status': 'success'})
    
    return JsonResponse({'status': 'error'}, status=400)

# Optional view to get the CSRF token (used in JavaScript)
def csrf_token(request):
    return JsonResponse({'csrfToken': get_token(request)})
    
# Profile View
@login_required
@csrf_protect
def profile(request):
    if not hasattr(request.user, 'profile'):
        Profile.objects.create(user=request.user)

    if request.method == 'POST':
        user_form = UserUpdateForm(request.POST, instance=request.user)
        profile_form = ProfileUpdateForm(request.POST, request.FILES, instance=request.user.profile)
        if user_form.is_valid() and profile_form.is_valid():
            user_form.save()
            profile_form.save()
            messages.success(request, 'Your profile has been updated successfully!')
            return redirect('profile')
        else:
            messages.error(request, 'Please correct the errors below.')
    else:
        user_form = UserUpdateForm(instance=request.user)
        profile_form = ProfileUpdateForm(instance=request.user.profile)

    return render(request, 'users/profile.html', {'user_form': user_form, 'profile_form': profile_form})

# Signup View
# @csrf_protect
def signup_view(request):
    if request.method == 'POST':
        form = CustomUserCreationForm(request.POST)
        if form.is_valid():
            user = form.save()
            login(request, user)
            next_page = request.session.get('next_page', 'index')
            return redirect(next_page)
    else:
        form = CustomUserCreationForm()
    return render(request, 'signup.html', {'form': form})

# Login View
@csrf_protect
def login_view(request):
    if request.method == 'POST':
        form = CustomLoginForm(request, data=request.POST)
        if form.is_valid():
            username = form.cleaned_data.get('username')
            password = form.cleaned_data.get('password')
            user = authenticate(username=username, password=password)
            if user is not None:
                login(request, user)

                # Check if the user is a superuser
                if user.is_superuser:
                    return redirect(reverse('admin:index'))  # Redirect to the admin dashboard

                next_page = request.session.get('next_page', 'index')
                request.session.pop('next_page', None)
                return redirect(next_page)
    else:
        form = CustomLoginForm()
        
    return render(request, 'login.html', {'form': form})
# Some View (Example View)
@csrf_protect
def some_view(request):
    # Filter to exclude admin (superusers) from profiles
    profiles = Profile.objects.filter(user__is_superuser=False)

    if request.user.is_authenticated:
        return redirect('checkout')
    else:
        request.session['next_page'] = request.path
        return redirect('login')

    # Render a template with profiles if not redirecting
    return render(request, 'some_template.html', {'profiles': profiles})

# Shipping Fee Calculation Function
def calculate_shipping_fee(order):
    total_price = order.calculate_total_price()  # Returns the total price of the order
    if total_price < 50:
        return 10  # Flat fee for orders below $50
    elif total_price < 100:
        return 5   # Discounted fee for orders between $50 and $100
    else:
        return 0   # Free shipping for orders $100 and above

# Check if User is Logged In
def is_logged_in(request):
    return JsonResponse({'is_authenticated': request.user.is_authenticated})

# Checkout View
@login_required
@csrf_protect
def checkout_view(request):
    cart = Cart.objects.get(user=request.user)
    cart_items = CartItem.objects.filter(cart=cart)

    if request.method == 'POST':
        form = CheckoutForm(request.POST)
        payment_method = request.POST.get('payment_method')

        if form.is_valid():
            # Create order
            order = Order.objects.create(user=request.user)
            # Calculate and set the shipping fee
            order.shipping_fee = calculate_shipping_fee(order)
            order.total_price = order.calculate_total_price() + order.shipping_fee  # Include shipping fee in total price
            order.save()

            # Create order items
            for item in cart_items:
                OrderItem.objects.create(order=order, product=item.product, quantity=item.quantity, price=item.product.price)

            # Save shipping details
            shipping_details = form.save(commit=False)
            shipping_details.order = order
            shipping_details.save()
            # Handle payment method (no real payment processing here)
            # Payment.objects.create(
                # order=order,
                # payment_method=payment_method,
                # amount=order.total_price,
                # transaction_id="N/A",  # Placeholder, not real transaction ID
                # payment_status="pending"  # You can set this as 'pending' or other status
            # )

            # Clear cart
            cart_items.delete()

            return redirect('order_confirmation', order_id=order.id)
    else:
        form = CheckoutForm()

    context = {
        'form': form,
        'cart_items': cart_items,
        'cart': cart,
        'total_price': cart.get_total(),
    }
    return render(request, 'checkout.html', context)

# Logout View
@csrf_protect
def logout_view(request):
    logger.debug(f"Request method: {request.method}")
    if request.method == 'POST':
        logout(request)
        return redirect('login')
    else:
        return HttpResponseForbidden("Only POST requests are allowed for logout.")

# Place Order View
@login_required
@csrf_protect
def place_order(request):
    if request.method == 'POST':
        cart = Cart.objects.get(user=request.user)
        cart_items = CartItem.objects.filter(cart=cart)

        if not cart_items.exists():
            return JsonResponse({'status': 'error', 'message': 'Your cart is empty.'}, status=400)

        try:
            # Create Order
            order = Order.objects.create(user=request.user)
            for item in cart_items:
                OrderItem.objects.create(order=order, product=item.product, quantity=item.quantity, price=item.product.price)
            
            # Calculate and set the shipping fee
            order.shipping_fee = calculate_shipping_fee(order)
            order.total_price = order.calculate_total_price() + order.shipping_fee
            order.save()

            # Clear Cart
            cart_items.delete()

            # Redirect to Order Confirmation
            return redirect('order_confirmation', order_id=order.id)
        except Exception as e:
            logger.error(f"Error placing order: {e}")
            return JsonResponse({'status': 'error', 'message': 'An error occurred while placing your order.'}, status=500)
    else:
        return HttpResponseBadRequest("Invalid request method.")

# Order Confirmation View
@login_required
def order_confirmation(request, order_id):
    order = get_object_or_404(Order, id=order_id, user=request.user)
    return render(request, 'order_confirmation.html', {'order': order})

# print(reverse('update_cart'))