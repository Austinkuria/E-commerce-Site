from django.shortcuts import render, get_object_or_404, redirect
from django.http import HttpResponse, JsonResponse, HttpResponseBadRequest,HttpResponseRedirect
from django.contrib.auth import authenticate, logout, login, login as auth_login
from django.contrib.auth.decorators import login_required
from django.views.decorators.csrf import csrf_protect
from .models import Product, Cart, CartItem, Order, OrderItem, Profile, Payment, ShippingDetails
from .forms import CustomUserCreationForm, CustomLoginForm, UserUpdateForm, ProfileUpdateForm, CheckoutForm
from django.contrib import messages 
import logging
from django.middleware.csrf import get_token
from django.core.mail import send_mail
from django.conf import settings

# Set up logging to track events and errors
logger = logging.getLogger(__name__)

# View to list all products on the index page
def products_view(request):
    if request.user.is_authenticated:
        # If the user is logged in, retrieve their cart from the database or create a new one if it doesn’t exist
        cart, created = Cart.objects.get_or_create(user=request.user)
        cart_items = CartItem.objects.filter(cart=cart)  # Get all items in the user’s cart
    else:
        # If the user is not logged in, retrieve the cart from the session data
        cart = request.session.get('cart', {})
        cart_items = [
            {
                'product': get_object_or_404(Product, id=int(product_id)),  # Fetch product details by ID
                'quantity': item['quantity'],  # Quantity of the product
                'price': item['price'],  # Price of the product
                'total_price': item['price'] * item['quantity']  # Calculate total price for the product
            }
            for product_id, item in cart.items()  # Iterate over each item in the session cart
        ]

    # Fetch all products from the database
    products = Product.objects.all()
    context = {
        'products': products,  # Provide products to the template
        'cart_items': cart_items  # Provide cart items to the template
    }
    return render(request, 'index.html', context)  # Render the template with the given context

# View to get the current user's cart items
@csrf_protect
def get_cart(request):
    if request.user.is_authenticated:
        # For authenticated users, get the cart from the database
        cart, created = Cart.objects.get_or_create(user=request.user)
        cart_items = CartItem.objects.filter(cart=cart)  # Retrieve all cart items
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
        # For anonymous users, get the cart from session data
        cart = request.session.get('cart', {})
        cart_items_data = [
            {
                'id': int(product_id),  # Product ID
                'name': item['name'],  # Product name
                'price': item['price'],  # Product price
                'quantity': item['quantity'],  # Quantity
                'image': item.get('image')  # Image URL (if available)
            }
            for product_id, item in cart.items()  # Iterate over session cart items
        ]

    # Return cart items data as JSON response
    return JsonResponse({'cart_items': cart_items_data})

# View to handle adding a product to the cart
@csrf_protect
def add_to_cart(request):
    if request.method == 'POST':
        try:
            # Extract product ID and quantity from the POST request
            product_id = int(request.POST.get('product_id'))
            quantity = int(request.POST.get('quantity'))
        except (TypeError, ValueError):
            # Return error if product ID or quantity is invalid
            return JsonResponse({'status': 'error', 'message': 'Invalid product ID or quantity'}, status=400)

        # Fetch product from the database or return a 404 if not found
        product = get_object_or_404(Product, id=product_id)

        if request.user.is_authenticated:
            # For logged-in users, handle cart in the database
            cart, created = Cart.objects.get_or_create(user=request.user)
            cart_item, created = CartItem.objects.get_or_create(cart=cart, product=product)
            if not created:
                cart_item.quantity += quantity  # Update quantity if item already exists
            else:
                cart_item.quantity = quantity  # Set quantity if new item
            cart_item.save()  # Save changes to the database
        else:
            # For anonymous users, handle cart in session data
            cart = request.session.get('cart', {})
            if str(product_id) in cart:
                cart[str(product_id)]['quantity'] += quantity  # Update quantity in session cart
            else:
                cart[str(product_id)] = {
                    'name': product.name,
                    'price': float(product.price),
                    'quantity': quantity,
                    'image': product.image.url
                }
            request.session['cart'] = cart  # Save updated cart to session

        return JsonResponse({'status': 'success', 'message': 'Item added to cart successfully'})

    return JsonResponse({'status': 'error', 'message': 'Invalid request method'}, status=400)

# View to handle removing a product from the cart
@csrf_protect
def remove_from_cart(request):
    if request.method == 'POST':
        try:
            # Extract product ID from POST request
            product_id = int(request.POST.get('product_id'))
        except (TypeError, ValueError):
            return JsonResponse({'status': 'error', 'message': 'Invalid product ID'}, status=400)
        
        if request.user.is_authenticated:
            # For logged-in users, handle cart in the database
            cart = get_object_or_404(Cart, user=request.user)
            product = get_object_or_404(Product, id=product_id)
            
            try:
                cart_item = CartItem.objects.get(cart=cart, product=product)  # Get the cart item
                cart_item.delete()  # Remove the item from the cart
                return JsonResponse({'status': 'success'})
            except CartItem.DoesNotExist:
                return JsonResponse({'status': 'error', 'message': 'Item not found in cart'}, status=404)
        else:
            # For anonymous users, handle cart in session data
            cart = request.session.get('cart', {})
            if str(product_id) in cart:
                del cart[str(product_id)]  # Remove item from session cart
                request.session['cart'] = cart
                return JsonResponse({'status': 'success'})
            else:
                return JsonResponse({'status': 'error', 'message': 'Item not found in cart'}, status=404)
    
    return JsonResponse({'status': 'error', 'message': 'Invalid request method'}, status=400)

# View to update the quantity of a product in the cart
@csrf_protect
def update_cart(request):
    if request.method == 'POST':
        # Extract product ID and action ('increase' or 'decrease') from POST request
        product_id = int(request.POST.get('product_id'))
        action = request.POST.get('action')
        
        if request.user.is_authenticated:
            # For logged-in users, handle cart in the database
            cart = get_object_or_404(Cart, user=request.user)
            product = get_object_or_404(Product, id=product_id)
            cart_item, created = CartItem.objects.get_or_create(cart=cart, product=product)
            
            if action == 'increase':
                cart_item.quantity += 1  # Increase quantity
            elif action == 'decrease':
                cart_item.quantity -= 1  # Decrease quantity
            
            if cart_item.quantity <= 0:
                cart_item.delete()  # Remove item if quantity is 0 or less
            else:
                cart_item.save()  # Save changes if item is still in the cart
            
            return JsonResponse({'status': 'success'})
        else:
            # For anonymous users, handle cart in session data
            cart = request.session.get('cart', {})
            if str(product_id) in cart:
                if action == 'increase':
                    cart[str(product_id)]['quantity'] += 1  # Increase quantity
                elif action == 'decrease':
                    cart[str(product_id)]['quantity'] -= 1  # Decrease quantity
                
                if cart[str(product_id)]['quantity'] <= 0:
                    del cart[str(product_id)]  # Remove item if quantity is 0 or less
                
                request.session['cart'] = cart  # Save updated cart to session
                return JsonResponse({'status': 'success'})
            
            return JsonResponse({'status': 'error', 'message': 'Item not found in cart'}, status=404)
    
    # Return error for non-POST requests
    return JsonResponse({'status': 'error'}, status=400)

# View to provide the CSRF token for JavaScript to use
def csrf_token(request):
    return JsonResponse({'csrfToken': get_token(request)})  # Return CSRF token as JSON

# View to display and update user profile
@login_required
@csrf_protect
def profile(request):
    if not hasattr(request.user, 'profile'):
        Profile.objects.create(user=request.user)  # Create profile if it doesn't exist

    if request.method == 'POST':
        user_form = UserUpdateForm(request.POST, instance=request.user)
        profile_form = ProfileUpdateForm(request.POST, request.FILES, instance=request.user.profile)
        
        if user_form.is_valid() and profile_form.is_valid():
            user_form.save()
            profile_form.save()
            # Add success message
            messages.success(request, 'Your profile has been updated successfully.')
            return redirect('profile')
        else:
            # If form is invalid, add error message
            messages.error(request, 'Please correct the error below.')

    else:
        user_form = UserUpdateForm(instance=request.user)
        profile_form = ProfileUpdateForm(instance=request.user.profile)

    return render(request, 'users/profile.html', {'user_form': user_form, 'profile_form': profile_form})

# View to handle user registration
@csrf_protect
def signup_view(request):
    if request.method == 'POST':
        form = CustomUserCreationForm(request.POST)  # Form for user registration
        if form.is_valid():
            user = form.save()  # Save new user
            login(request, user)  # Log in the newly registered user
            next_page = request.session.get('next_page', 'index')  # Get the next page to redirect to
            return redirect(next_page)  # Redirect to the next page
        else:
            return render(request, 'user_auth/signup.html', {'form': form})  # Render registration page with errors if form is not valid
    else:
        form = CustomUserCreationForm()  # Empty form for GET request

    return render(request, 'user_auth/signup.html', {'form': form})  # Render registration page with form

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
                auth_login(request, user)  # Log in the user
                
                # Sync session cart with database cart if needed
                if 'cart' in request.session:
                    cart = request.session.get('cart')
                    db_cart, created = Cart.objects.get_or_create(user=user)
                    for product_id, item in cart.items():
                        product = get_object_or_404(Product, id=int(product_id))
                        cart_item, created = CartItem.objects.get_or_create(cart=db_cart, product=product)
                        cart_item.quantity = item['quantity']
                        cart_item.save()
                    del request.session['cart']  # Clear session cart after syncing
                
                # Redirect based on user role
                if user.is_superuser:
                    return redirect('/admin/')  # Redirect to admin page if user is a superuser
                else:
                    return redirect('index')  # Redirect to index page otherwise
            else:
                form.add_error(None, 'Please enter a correct username and password. Note that both fields may be case-sensitive.')
        else:
            if not form.non_field_errors():
                form.add_error(None, 'Please correct the errors below.')
    else:
        form = CustomLoginForm()

    return render(request, 'registration/login.html', {'form': form})  # Render login page with form

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
        logout(request)  # Log out the user
        return redirect('index')  # Redirect to the index page after logout
    
    return render(request, 'log_out.html')  # Render logout page

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
        cart_items = []  # Initialize list to hold cart items
        total_price = 0  # Initialize total price
        shipping_fee = 0  # Initialize shipping fee

        # Get product details from GET parameters
        product_id = request.GET.get('product_id')
        product_name = request.GET.get('product_name')
        product_price = request.GET.get('product_price')
        product_quantity = int(request.GET.get('product_quantity', 1))  # Default quantity to 1 if not provided

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
        else:
            if request.user.is_authenticated:
                cart = get_object_or_404(Cart, user=request.user)
                cart_items = CartItem.objects.filter(cart=cart)
                if not cart_items:
                    return render(request, 'empty_cart.html')
                total_price = sum(item.get_total_price() for item in cart_items)
            else:
                cart = request.session.get('cart', {})
                if not cart:
                    return render(request, 'empty_cart.html')
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

        # Pre-fill form with user's saved info if available
        initial_data = {}
        if request.user.is_authenticated:
            # If the user's profile or address info is stored in the `request.user.profile`
            profile = request.user.profile
            initial_data = {
                'phone_number':profile.phone_number,
                'address': profile.address,
                'city': profile.city,
                'postal_code': profile.postal_code,
            }

        form = CheckoutForm(initial=initial_data)

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
            phone_number = form.cleaned_data.get('phone_number')
            
            # Update the user's profile if it has no shipping info yet
            profile = request.user.profile
            if not profile.address:
                profile.address = address
            if not profile.city:
                profile.city = city
            if not profile.postal_code:
                profile.postal_code = postal_code
            if not profile.phone_number:
                profile.phone_number = phone_number
            profile.save()  # Save changes to the profile

            product_data = request.session.get('checkout_product')

            if product_data:
                try:
                    product = Product.objects.get(id=product_data['product_id'])
                    item_total = product_data['product_price'] * product_data['product_quantity']
                    shipping_fee = calculate_shipping_fee(item_total)
                    total = item_total + shipping_fee

                    order = Order.objects.create(
                        user=request.user,
                        address=address,
                        city=city,
                        postal_code=postal_code,
                        total=total,
                    )
                    OrderItem.objects.create(
                        order=order,
                        product=product,
                        quantity=product_data['product_quantity'],
                        price=product_data['product_price']
                    )
                    del request.session['checkout_product']
                    return redirect('order_confirmation', order_id=order.id)
                except Product.DoesNotExist:
                    return HttpResponse("Product not found.", status=404)
            else:
                if request.user.is_authenticated:
                    cart = get_object_or_404(Cart, user=request.user)
                    cart_items = CartItem.objects.filter(cart=cart)
                    if not cart_items:
                        return render(request, 'empty_cart.html')
                else:
                    cart = request.session.get('cart', {})
                    if not cart:
                        return render(request, 'empty_cart.html')
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

                total_price = sum(item.get_total_price() for item in cart_items)
                shipping_fee = calculate_shipping_fee(total_price)
                total_price += shipping_fee

                order = Order.objects.create(
                    user=request.user,
                    address=address,
                    city=city,
                    postal_code=postal_code,
                    total=total_price,
                )

                for item in cart_items:
                    OrderItem.objects.create(
                        order=order,
                        product=item.product,
                        quantity=item.quantity,
                        price=item.product.price
                    )

                if request.user.is_authenticated:
                    CartItem.objects.filter(cart=cart).delete()
                else:
                    request.session['cart'] = {}

                return redirect('order_confirmation', order_id=order.id)
        else:
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

                total_price = sum(item.get_total_price() for item in cart_items)
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

            # Calculate total price and shipping fee
            total_price = sum(item.product.price * item.quantity for item in cart_items)
            shipping_fee = calculate_shipping_fee(total_price)
            total_with_shipping = total_price + shipping_fee

            # Create and save the order with shipping fee
            order = Order.objects.create(
                user=request.user,
                shipping_fee=shipping_fee,
                total=total_with_shipping,
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
            cart_items.delete()  # Remove items from the database cart

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
    
    # Calculate total price including shipping fee
    total_price = sum(item.price for item in order_items)  # Item price includes quantity
    shipping_fee =  calculate_shipping_fee(total_price)
    final_total = total_price + shipping_fee

    context = {
        'order': order,
        'order_items': order_items,
        'shipping_fee': shipping_fee,
        'total_price': final_total,
    }

    # Render the order confirmation page with the context data
    return render(request, 'order_confirmation.html', context)
    
def about_us(request):
    return render(request, 'about_us.html')

def contact(request):
    return render(request, 'contact.html')

def privacy_policy(request):
    return render(request, 'privacy_policy.html')

def terms_of_service(request):
    return render(request, 'terms_of_service.html')

def shipping_information(request):
    return render(request, 'shipping_information.html')

def returns_exchanges(request):
    return render(request, 'returns_exchanges.html')

def faq(request):
    return render(request, 'faq.html')

def track_order_view(request):
    if request.method == 'POST':
        order_number = request.POST.get('order_number')
        email = request.POST.get('email')

        # Retrieve the order by order number and user email
        try:
            order = Order.objects.get(id=order_number, user__email=email)
            order_status = order.status  
            
            # Retrieve the order items and get product names
            order_items = order.items.all()  # Use related_name 'items' to access OrderItem objects
            products = [{'name': item.product.name, 'quantity': item.quantity} for item in order_items]
            
            context = {
                'order': order,
                'order_status': order_status,
                'products': products,  # Pass the products and their quantities to the template
            }
            return render(request, 'track_order.html', context)

        except Order.DoesNotExist:
            context = {
                'error_message': "Order not found. Please check your order number and email address."
            }
            return render(request, 'track_order.html', context)

    return render(request, 'track_order.html')
