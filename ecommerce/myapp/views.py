from django.shortcuts import render, get_object_or_404, redirect
from django.http import JsonResponse, HttpResponseBadRequest,HttpResponseRedirect
from django.contrib import messages
from django.contrib.auth import authenticate, login,logout
from django.contrib.auth.decorators import login_required
from django.views.decorators.csrf import csrf_protect
from .models import Product, Cart, CartItem, Order, OrderItem, Profile, Payment, ShippingDetails
from .forms import CustomUserCreationForm, CustomLoginForm, UserUpdateForm, ProfileUpdateForm, CheckoutForm
import logging

from django.middleware.csrf import get_token
from decimal import Decimal
logger = logging.getLogger(__name__)

# View to list all products on the home page
def products_view(request):
    products = Product.objects.all()  # Retrieve all products from the database
    return render(request, 'index.html', {'products': products})  # Render the product list on the home page

# View to get the current user's cart items
@csrf_protect
def get_cart(request):
    if request.user.is_authenticated:
        # For authenticated users, retrieve cart from the database
        cart = get_object_or_404(Cart, user=request.user)
        cart_items = CartItem.objects.filter(cart=cart)
        cart_items_data = [
            {
                'id': item.product.id,
                'name': item.product.name,
                'price': item.product.price,
                'quantity': item.quantity
            }
            for item in cart_items
        ]
    else:
        # For anonymous users, retrieve cart from the session
        cart = request.session.get('cart', {})
        cart_items_data = [
            {
                'id': int(product_id),
                'name': item['name'],
                'price': item['price'],
                'quantity': item['quantity'],
                'image': item.get('image')
            }
            for product_id, item in cart.items()
        ]

    return JsonResponse({'cart_items': cart_items_data})

# View to handle adding a product to the cart
@csrf_protect
def add_to_cart(request):
    if request.method == 'POST':
        try:
            # Extract product_id and quantity from POST request
            product_id = int(request.POST.get('product_id'))
            quantity = int(request.POST.get('quantity'))
        except (TypeError, ValueError):
            return JsonResponse({'status': 'error', 'message': 'Invalid product ID or quantity'}, status=400)

        # Retrieve the product or return a 404 if not found
        product = get_object_or_404(Product, id=product_id)

        if request.user.is_authenticated:
            # For authenticated users, use the database cart
            cart, created = Cart.objects.get_or_create(user=request.user)
            cart_item, created = CartItem.objects.get_or_create(cart=cart, product=product)
            if not created:
                cart_item.quantity += quantity  # Update quantity if item already exists
            else:
                cart_item.quantity = quantity  # Set initial quantity if item is new
            cart_item.save()
        else:
            # For anonymous users, use the session-based cart
            cart = request.session.get('cart', {})
            if str(product_id) in cart:
                cart[str(product_id)]['quantity'] += quantity
            else:
                cart[str(product_id)] = {
                    'name': product.name,
                    'price': float(product.price),  # Convert Decimal to float
                    'quantity': quantity,
                    'image': product.image.url
                }
            request.session['cart'] = cart

        return JsonResponse({'status': 'success', 'message': 'Item added to cart successfully'})

    return JsonResponse({'status': 'error', 'message': 'Invalid request method'}, status=400)

# View to handle removing a product from the cart
@csrf_protect
def remove_from_cart(request):
    if request.method == 'POST':
        try:
            # Extract product_id from POST request
            product_id = int(request.POST.get('product_id'))
        except (TypeError, ValueError):
            return JsonResponse({'status': 'error', 'message': 'Invalid product ID'}, status=400)
        
        if request.user.is_authenticated:
            # For authenticated users, use the database cart
            cart = get_object_or_404(Cart, user=request.user)
            product = get_object_or_404(Product, id=product_id)
            
            try:
                # Try to retrieve the cart item for the product
                cart_item = CartItem.objects.get(cart=cart, product=product)
                cart_item.delete()  # Remove the item from the cart
                return JsonResponse({'status': 'success'})
            except CartItem.DoesNotExist:
                return JsonResponse({'status': 'error', 'message': 'Item not found in cart'}, status=404)
        else:
            # For anonymous users, use the session-based cart
            cart = request.session.get('cart', {})
            if str(product_id) in cart:
                del cart[str(product_id)]  # Remove the item from the session cart
                request.session['cart'] = cart
                return JsonResponse({'status': 'success'})
            else:
                return JsonResponse({'status': 'error', 'message': 'Item not found in cart'}, status=404)
    
    return JsonResponse({'status': 'error', 'message': 'Invalid request method'}, status=400)
# View to update the quantity of a product in the cart
@csrf_protect
def update_cart(request):
    if request.method == 'POST':
        # Extract product_id and action ('increase' or 'decrease') from POST request
        product_id = int(request.POST.get('product_id'))
        action = request.POST.get('action')
        
        if request.user.is_authenticated:
            # For authenticated users, use the database cart
            cart = get_object_or_404(Cart, user=request.user)
            product = get_object_or_404(Product, id=product_id)
            cart_item, created = CartItem.objects.get_or_create(cart=cart, product=product)
            
            if action == 'increase':
                # Increase quantity if action is 'increase'
                cart_item.quantity += 1
            elif action == 'decrease':
                # Decrease quantity if action is 'decrease'
                cart_item.quantity -= 1
            
            if cart_item.quantity <= 0:
                # Remove item if quantity drops to 0 or below
                cart_item.delete()
            else:
                # Save the updated quantity if item is still in the cart
                cart_item.save()
            
            return JsonResponse({'status': 'success'})
        else:
            # For anonymous users, use the session-based cart
            cart = request.session.get('cart', {})
            if str(product_id) in cart:
                if action == 'increase':
                    cart[str(product_id)]['quantity'] += 1
                elif action == 'decrease':
                    cart[str(product_id)]['quantity'] -= 1
                
                # Remove the item from the session cart if quantity is 0 or below
                if cart[str(product_id)]['quantity'] <= 0:
                    del cart[str(product_id)]
                
                request.session['cart'] = cart
                return JsonResponse({'status': 'success'})
            
            return JsonResponse({'status': 'error', 'message': 'Item not found in cart'}, status=404)
    
    # Return an error for non-POST requests
    return JsonResponse({'status': 'error'}, status=400)
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
        form = CustomLoginForm(request, data=request.POST)
        if form.is_valid():
            username = form.cleaned_data.get('username')
            password = form.cleaned_data.get('password')
            user = authenticate(username=username, password=password)
            if user is not None:
                login(request, user)
                next_page = request.session.get('next_page', 'index')
                request.session.pop('next_page', None)
                return redirect(next_page)
            else:
                messages.error(request, 'Invalid username or password.')
        else:
            messages.error(request, 'Please correct the errors below.')
    else:
        form = CustomLoginForm()

    return render(request, 'registration/login.html', {'form': form})

# View to redirect authenticated users to checkout or login for unauthenticated users
@csrf_protect
def some_view(request):
    if request.user.is_authenticated:
        return redirect('checkout')  # Redirect authenticated users to checkout page
    else:
        request.session['next_page'] = request.path  # Save current path to session
        return redirect('login')  # Redirect unauthenticated users to login page

# View to handle logout
def log_out(request):
    if request.method == 'POST':
        logout(request)
        return redirect('index')  # Redirects to the index page after logout
    
    return render(request, 'log_out.html')
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
        # Try to get the cart associated with the current user.
        cart = Cart.objects.get(user=request.user)
    except Cart.DoesNotExist:
        # If the cart does not exist, create a new cart for the user.
        cart = Cart.objects.create(user=request.user)

    # Get all items in the cart for the current user.
    cart_items = CartItem.objects.filter(cart=cart)

    # If the cart is empty, render a template to notify the user.
    if not cart_items.exists():
        return render(request, 'empty_cart.html')  # Render a template to show the alert

    if request.method == 'POST':
        # Create a form instance with the submitted POST data.
        form = CheckoutForm(request.POST)
        # Retrieve the selected payment method from the POST data.
        payment_method = request.POST.get('payment_method')

        if form.is_valid():
            # Calculate the total price of the items in the cart.
            total_price = cart.get_total_price()
            # Calculate the shipping fee based on the total price.
            shipping_fee = calculate_shipping_fee(total_price)

            # Create a new order record with the total price and shipping fee.
            order = Order.objects.create(
                user=request.user,
                total=total_price + shipping_fee,
                address=form.cleaned_data['address'],
                city=form.cleaned_data['city'],
                postal_code=form.cleaned_data['postal_code']
            )

            # Update the order with the shipping fee.
            order.shipping_fee = shipping_fee
            order.save()

            # Create OrderItem records for each item in the cart.
            for item in cart_items:
                OrderItem.objects.create(order=order, product=item.product, quantity=item.quantity)

            # Create or update shipping details for the user.
            shipping_details, created = ShippingDetails.objects.get_or_create(
                user=request.user,
                defaults={
                    'order': order,
                    'address': form.cleaned_data['address'],
                    'city': form.cleaned_data['city'],
                    'postal_code': form.cleaned_data['postal_code']
                }
            )

            if not created:
                # If shipping details already exist, update them with new data.
                shipping_details.address = form.cleaned_data['address']
                shipping_details.city = form.cleaned_data['city']
                shipping_details.postal_code = form.cleaned_data['postal_code']
                shipping_details.save()

            # Create a payment record with the details of the payment.
            Payment.objects.create(
                order=order,
                payment_method=payment_method,
                amount=order.total,
                transaction_id="N/A",
                payment_status="pending"
            )

            # Clear all items from the cart after checkout is complete.
            cart_items.delete()

            # Redirect to the order confirmation page.
            return redirect('order_confirmation', order_id=order.id)
    else:
        # If the request method is not POST, create an empty form.
        form = CheckoutForm()

    # Calculate the total price and shipping fee to display in the checkout page.
    total_price = cart.get_total_price()
    shipping_fee = calculate_shipping_fee(total_price)

    # Prepare the context for rendering the checkout page.
    context = {
        'form': form,
        'cart_items': cart_items,
        'shipping_fee': shipping_fee,
        'total_price': total_price + shipping_fee,
    }
    # Render the checkout page with the provided context.
    return render(request, 'checkout.html', context)

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
