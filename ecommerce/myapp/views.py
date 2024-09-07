from django.shortcuts import render, get_object_or_404, redirect
from django.http import HttpResponse, JsonResponse, HttpResponseBadRequest,HttpResponseRedirect
from django.contrib import messages
from django.contrib.auth import authenticate, logout, login, login as auth_login
from django.contrib.auth.decorators import login_required
from django.views.decorators.csrf import csrf_protect
from .models import Product, Cart, CartItem, Order, OrderItem, Profile, Payment, ShippingDetails
from .forms import CustomUserCreationForm, CustomLoginForm, UserUpdateForm, ProfileUpdateForm, CheckoutForm
import logging
from django.db.models import Sum
from django.middleware.csrf import get_token
from decimal import Decimal
logger = logging.getLogger(__name__)
from django.utils import timezone



# View to list all products on the home page
def products_view(request):
    products = Product.objects.all()  # Retrieve all products from the database
    return render(request, 'index.html', {'products': products})  # Render the product list on the home page

# View to get the current user's cart items
@csrf_protect
def get_cart(request):
    # Check if the user is authenticated (logged in)
    if request.user.is_authenticated:
        # Try to get the cart for the authenticated user; if it doesn't exist, create one
        cart, created = Cart.objects.get_or_create(user=request.user)
        # Retrieve all items in the user's cart
        cart_items = CartItem.objects.filter(cart=cart)
        # Prepare a list of cart item details to return in JSON response
        cart_items_data = [
            {
                'id': item.product.id,  # Product ID
                'name': item.product.name,  # Product name
                'price': item.product.price,  # Product price
                'quantity': item.quantity,  # Quantity of the product in the cart
                'image': item.product.image.url  # URL of the product image
            }
            for item in cart_items
        ]
    else:
        # If the user is not logged in, retrieve the cart from the session
        cart = request.session.get('cart', {})
        # Prepare a list of cart item details stored in the session
        cart_items_data = [
            {
                'id': int(product_id),  # Product ID stored in session
                'name': item['name'],  # Product name stored in session
                'price': item['price'],  # Product price stored in session
                'quantity': item['quantity'],  # Quantity of the product stored in session
                'image': item.get('image')  # Image URL stored in session (if available)
            }
            for product_id, item in cart.items()
        ]

    # Return the cart items in JSON format
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
                auth_login(request, user)
                # Check if the user is a superuser or not
                if user.is_superuser:
                    # Redirect to the admin page
                    return redirect('/admin/')
                else:
                    # Redirect to the index page
                    return redirect('index')  # Ensure 'index' is the correct name of your index view
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

# View to handle the checkout process
@login_required
@csrf_protect
def checkout_view(request):
    if request.method == 'GET':
        cart_items = []
        total_price = 0
        shipping_fee = 0

        # Get product details from GET parameters
        product_id = request.GET.get('product_id')
        product_name = request.GET.get('product_name')
        product_price = request.GET.get('product_price')
        product_quantity = int(request.GET.get('product_quantity', 1))

        if product_id and product_name and product_price:
            try:
                product = Product.objects.get(id=product_id)
                product_price = float(product_price)
                total_price = product_price * product_quantity
                shipping_fee = calculate_shipping_fee(total_price)

                # Store product details in session for use in POST
                request.session['checkout_product'] = {
                    'product_id': product_id,
                    'product_name': product_name,
                    'product_price': product_price,
                    'product_quantity': product_quantity,
                }

                cart_items = [{
                    'quantity': product_quantity,
                    'product': {
                        'name': product_name,
                        'price': product_price,
                        'description': request.GET.get('product_description'),
                    },
                    'get_total_price': product_price * product_quantity,
                }]
            except Product.DoesNotExist:
                return HttpResponse("Product not found.", status=404)
            except ValueError:
                return HttpResponse("Invalid price format.", status=400)

        else:
            # Handle cart-based checkout
            if request.user.is_authenticated:
                cart, created = Cart.objects.get_or_create(user=request.user)
                cart_items = CartItem.objects.filter(cart=cart)
                total_price = sum(item.product.price * item.quantity for item in cart_items)
            else:
                cart = request.session.get('cart', {})
                for product_id, item in cart.items():
                    try:
                        product = Product.objects.get(id=product_id)
                        cart_items.append({
                            'quantity': item['quantity'],
                            'product': {
                                'name': product.name,
                                'price': item['price'],
                            },
                            'get_total_price': item['quantity'] * item['price'],
                        })
                    except Product.DoesNotExist:
                        continue
                total_price = sum(item['get_total_price'] for item in cart_items)

        shipping_fee = calculate_shipping_fee(total_price)
        total_price += shipping_fee

        form = CheckoutForm()

        context = {
            'form': form,
            'cart_items': cart_items,
            'total_price': total_price,
            'shipping_fee': shipping_fee,
        }
        return render(request, 'checkout.html', context)

    elif request.method == 'POST':
        form = CheckoutForm(request.POST)
        if form.is_valid():
            address = form.cleaned_data.get('address')
            city = form.cleaned_data.get('city')
            postal_code = form.cleaned_data.get('postal_code')

            # Retrieve product data from session if available
            product_data = request.session.get('checkout_product')

            if product_data:
                try:
                    product = Product.objects.get(id=product_data['product_id'])
                    order = Order.objects.create(
                        user=request.user,
                        address=address,
                        city=city,
                        postal_code=postal_code,
                        total=product_data['product_price'] * product_data['product_quantity'] + calculate_shipping_fee(product_data['product_price'] * product_data['product_quantity']),
                    )
                    OrderItem.objects.create(
                        order=order,
                        product=product,
                        quantity=product_data['product_quantity'],
                        price=product_data['product_price']
                    )
                    del request.session['checkout_product']  # Clear product data after successful order
                    return redirect('order_confirmation', order_id=order.id)
                except Product.DoesNotExist:
                    return HttpResponse("Product not found.", status=404)
            else:
                # Handle cart-based checkout
                if request.user.is_authenticated:
                    cart = get_object_or_404(Cart, user=request.user)
                    cart_items = CartItem.objects.filter(cart=cart)
                else:
                    cart = request.session.get('cart', {})
                    cart_items = []
                    for product_id, item in cart.items():
                        try:
                            product = Product.objects.get(id=product_id)
                            cart_items.append({
                                'quantity': item['quantity'],
                                'product': product,
                                'get_total_price': item['quantity'] * item['price'],
                            })
                        except Product.DoesNotExist:
                            continue

                total_price = sum(item['get_total_price'] for item in cart_items)
                shipping_fee = calculate_shipping_fee(total_price)

                order = Order.objects.create(
                    user=request.user,
                    address=address,
                    city=city,
                    postal_code=postal_code,
                    total=total_price + shipping_fee,
                )

                for item in cart_items:
                    OrderItem.objects.create(
                        order=order,
                        product=item['product'],
                        quantity=item['quantity'],
                        price=item['get_total_price']
                    )

                # Clear the cart after placing the order
                if request.user.is_authenticated:
                    cart_items.delete()
                else:
                    request.session['cart'] = {}

                return redirect('order_confirmation', order_id=order.id)
        else:
            # On validation error, retrieve data from session or cart
            product_data = request.session.get('checkout_product')
            if product_data:
                total_price = product_data['product_price'] * product_data['product_quantity']
                shipping_fee = calculate_shipping_fee(total_price)
                cart_items = [{
                    'quantity': product_data['product_quantity'],
                    'product': {
                        'name': product_data['product_name'],
                        'price': product_data['product_price'],
                    },
                    'get_total_price': total_price,
                }]
                total_price += shipping_fee
            else:
                if request.user.is_authenticated:
                    cart = get_object_or_404(Cart, user=request.user)
                    cart_items = CartItem.objects.filter(cart=cart)
                else:
                    cart = request.session.get('cart', {})
                    cart_items = []
                    for product_id, item in cart.items():
                        try:
                            product = Product.objects.get(id=product_id)
                            cart_items.append({
                                'quantity': item['quantity'],
                                'product': product,
                                'get_total_price': item['quantity'] * item['price'],
                            })
                        except Product.DoesNotExist:
                            continue

                total_price = sum(item['get_total_price'] for item in cart_items)
                shipping_fee = calculate_shipping_fee(total_price)
                total_price += shipping_fee

            context = {
                'form': form,
                'cart_items': cart_items,
                'total_price': total_price,
                'shipping_fee': shipping_fee,
            }
            return render(request, 'checkout.html', context)

# View to place an order and handle order creation
@login_required
@csrf_protect
def place_order(request):
    if request.method == 'POST':
        try:
            # Retrieve the user's cart and cart items
            cart = get_object_or_404(Cart, user=request.user)
            cart_items = CartItem.objects.filter(cart=cart)

            # Check if the cart is empty
            if not cart_items.exists():
                # Return an error message if the cart is empty
                return JsonResponse({'status': 'error', 'message': 'Your cart is empty.'}, status=400)

            # Calculate the total price of the cart items
            total_price = sum(item.product.price * item.quantity for item in cart_items)
            shipping_fee = calculate_shipping_fee(total_price)

            # Create and save the order with shipping fee
            order = Order.objects.create(
                user=request.user,
                shipping_fee=shipping_fee,
                total=total_price + shipping_fee,
            )

            # Create OrderItems for each item in the cart
            for item in cart_items:
                OrderItem.objects.create(
                    order=order,
                    product=item.product,
                    quantity=item.quantity,
                    price=item.product.price * item.quantity
                )

            # Clear the cart after placing the order
            cart_items.delete()

            # Redirect to the order confirmation page
            return redirect('order_confirmation', order_id=order.id)
        
        except Exception as e:
            # Log any errors that occur during order placement
            logger.error(f"Error placing order: {e}")
            # Return an error message if an exception is raised
            return JsonResponse({'status': 'error', 'message': 'An error occurred while placing your order.'}, status=500)
    else:
        # Handle invalid request method
        return HttpResponseBadRequest("Invalid request method.")

# View to display order confirmation
@login_required
def order_confirmation_view(request, order_id):
    # Retrieve the order using the order ID and ensure it belongs to the current user
    order = get_object_or_404(Order, id=order_id, user=request.user)
    
    # Retrieve all order items associated with the order
    order_items = order.items.all()
    
    # Calculate the total price of the order items
    total_price = sum(item.total_price for item in order_items)
    shipping_fee = calculate_shipping_fee(total_price)  # Calculate shipping fee based on total price

    context = {
        'order': order,
        'order_items': order_items,  # Pass order items to the template
        'total_price': total_price + shipping_fee,
        'shipping_fee': shipping_fee,
    }
    # Render the order confirmation page with the context data
    return render(request, 'order_confirmation.html', context)