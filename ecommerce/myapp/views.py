from django.shortcuts import render, get_object_or_404, redirect
from django.http import HttpResponse, JsonResponse, HttpResponseBadRequest,HttpResponseRedirect
from django.contrib.auth import authenticate, logout, login, login as auth_login
from django.contrib.auth.decorators import login_required
from django.views.decorators.csrf import csrf_protect
from .models import Product, Cart, CartItem, Order, OrderItem, Profile, Payment, ShippingDetails
from .forms import CustomUserCreationForm, CustomLoginForm, UserUpdateForm, ProfileUpdateForm, CheckoutForm
import logging
from django.db.models import Sum
from django.middleware.csrf import get_token


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
        user_form = UserUpdateForm(request.POST, instance=request.user)  # Form for updating user details
        profile_form = ProfileUpdateForm(request.POST, request.FILES, instance=request.user.profile)  # Form for updating profile details
        if user_form.is_valid() and profile_form.is_valid():
            user_form.save()  # Save updated user details
            profile_form.save()  # Save updated profile details
            return redirect('profile')  # Redirect to profile page
        else:
            return render(request, 'users/profile.html', {'user_form': user_form, 'profile_form': profile_form})  # Render profile page with errors if forms are not valid
    else:
        user_form = UserUpdateForm(instance=request.user)  # Prepopulate form with current user data
        profile_form = ProfileUpdateForm(instance=request.user.profile)  # Prepopulate form with current profile data

    return render(request, 'users/profile.html', {'user_form': user_form, 'profile_form': profile_form})  # Render profile page with forms

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
                # Try to retrieve the product from the database
                product = Product.objects.get(id=product_id)
                product_price = float(product_price)  # Convert price to float
                total_price = product_price * product_quantity  # Calculate total price for the product
                shipping_fee = calculate_shipping_fee(total_price)  # Calculate shipping fee based on total price

                # Store product details in session for use in POST
                request.session['checkout_product'] = {
                    'product_id': product_id,
                    'product_name': product_name,
                    'product_price': product_price,
                    'product_quantity': product_quantity,
                }

                # Add the product to the cart items list
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
                return HttpResponse("Product not found.", status=404)  # Return 404 if the product does not exist
            except ValueError:
                return HttpResponse("Invalid price format.", status=400)  # Return 400 if the price format is invalid
        else:
            # Handle checkout for items in the cart
            if request.user.is_authenticated:
                cart = get_object_or_404(Cart, user=request.user)  # Retrieve the cart for the logged-in user
                cart_items = CartItem.objects.filter(cart=cart)  # Get all items in the cart
                if not cart_items:
                    return render(request, 'empty_cart.html')  # Render empty cart page if no items are in the cart
                total_price = sum(item.get_total_price() for item in cart_items)  # Calculate total price
            else:
                cart = request.session.get('cart', {})  # Get cart from session data for anonymous users
                if not cart:
                    return render(request, 'empty_cart.html')  # Render empty cart page if no items are in the cart
                cart_items = []
                for product_id, item in cart.items():
                    try:
                        # Try to retrieve each product from the database
                        product = Product.objects.get(id=product_id)
                        cart_items.append({
                            'quantity': item['quantity'],
                            'product': product,
                            'get_total_price': item['quantity'] * item['price'],
                        })
                    except Product.DoesNotExist:
                        continue  # Skip if the product does not exist
                total_price = sum(item['get_total_price'] for item in cart_items)  # Calculate total price

        shipping_fee = calculate_shipping_fee(total_price)  # Calculate shipping fee
        total_price += shipping_fee  # Add shipping fee to total price

        form = CheckoutForm()  # Create a new checkout form

        context = {
            'form': form,
            'cart_items': cart_items,  # Pass cart items to the template
            'total_price': total_price,  # Pass total price to the template
            'shipping_fee': shipping_fee,  # Pass shipping fee to the template
        }
        return render(request, 'checkout.html', context)  # Render the checkout template with the context data

    elif request.method == 'POST':
        form = CheckoutForm(request.POST)  # Create a form instance with POST data
        if form.is_valid():
            address = form.cleaned_data.get('address')
            city = form.cleaned_data.get('city')
            postal_code = form.cleaned_data.get('postal_code')
            
            # Retrieve product data from session if available
            product_data = request.session.get('checkout_product')

            if product_data:
                try:
                    # Retrieve the product from the database
                    product = Product.objects.get(id=product_data['product_id'])
                    item_total = product_data['product_price'] * product_data['product_quantity']  # Calculate item total
                    shipping_fee = calculate_shipping_fee(item_total)  # Calculate shipping fee
                    total = item_total + shipping_fee  # Calculate total with shipping fee

                    # Create a new order
                    order = Order.objects.create(
                        user=request.user,
                        address=address,
                        city=city,
                        postal_code=postal_code,
                        total=total,
                    )
                    # Create an order item for the purchased product
                    OrderItem.objects.create(
                        order=order,
                        product=product,
                        quantity=product_data['product_quantity'],
                        price=product_data['product_price']
                    )
                    del request.session['checkout_product']  # Clear product data from session after successful order
                    return redirect('order_confirmation', order_id=order.id)  # Redirect to order confirmation page
                except Product.DoesNotExist:
                    return HttpResponse("Product not found.", status=404)  # Return 404 if the product does not exist
            else:
                # Handle cart-based checkout
                if request.user.is_authenticated:
                    cart = get_object_or_404(Cart, user=request.user)
                    cart_items = CartItem.objects.filter(cart=cart)
                    if not cart_items:
                        return render(request, 'empty_cart.html')  # Render empty cart page if no items are in the cart
                else:
                    cart = request.session.get('cart', {})
                    if not cart:
                        return render(request, 'empty_cart.html')  # Render empty cart page if no items are in the cart
                    cart_items = []
                    for product_id, item in cart.items():
                        try:
                            # Try to retrieve each product from the database
                            product = Product.objects.get(id=product_id)
                            cart_items.append({
                                'quantity': item['quantity'],
                                'product': product,
                                'get_total_price': item['quantity'] * item['price'],
                            })
                        except Product.DoesNotExist:
                            continue  # Skip if the product does not exist

                total_price = sum(item.get_total_price() for item in cart_items)  # Calculate total price
                shipping_fee = calculate_shipping_fee(total_price)  # Calculate shipping fee
                total_price += shipping_fee  # Add shipping fee to total price

                # Create a new order
                order = Order.objects.create(
                    user=request.user,
                    address=address,
                    city=city,
                    postal_code=postal_code,
                    total=total_price,
                )

                # Create order items for each item in the cart
                for item in cart_items:
                    OrderItem.objects.create(
                        order=order,
                        product=item.product,
                        quantity=item.quantity,
                        price=item.product.price
                    )

                # Clear the cart after placing the order
                if request.user.is_authenticated:
                    CartItem.objects.filter(cart=cart).delete()  # Remove items from the database cart
                else:
                    request.session['cart'] = {}  # Clear session cart

                return redirect('order_confirmation', order_id=order.id)  # Redirect to order confirmation page
        else:
            # On validation error, retrieve data from session or cart
            product_data = request.session.get('checkout_product')
            if product_data:
                total_price = product_data['product_price'] * product_data['product_quantity']  # Calculate total price
                shipping_fee = calculate_shipping_fee(total_price)  # Calculate shipping fee
                cart_items = [{
                    'quantity': product_data['product_quantity'],
                    'product': {
                        'name': product_data['product_name'],
                        'price': product_data['product_price'],
                    },
                    'get_total_price': total_price,
                }]
                total_price += shipping_fee  # Add shipping fee to total price
            else:
                if request.user.is_authenticated:
                    cart = get_object_or_404(Cart, user=request.user)
                    cart_items = CartItem.objects.filter(cart=cart)
                else:
                    cart = request.session.get('cart', {})
                    cart_items = []
                    for product_id, item in cart.items():
                        try:
                            # Try to retrieve each product from the database
                            product = Product.objects.get(id=product_id)
                            cart_items.append({
                                'quantity': item['quantity'],
                                'product': product,
                                'get_total_price': item['quantity'] * item['price'],
                            })
                        except Product.DoesNotExist:
                            continue  # Skip if the product does not exist

                total_price = sum(item['get_total_price'] for item in cart_items)  # Calculate total price
                shipping_fee = calculate_shipping_fee(total_price)  # Calculate shipping fee
                total_price += shipping_fee  # Add shipping fee to total price

            # Render checkout template with the form and context data
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
            shipping_fee = calculate_shipping_fee(total_price)  # Calculate shipping fee

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
    
    # Calculate the total price of the order items
    total_price = sum(item.total_price for item in order_items)
    shipping_fee = calculate_shipping_fee(total_price)  # Calculate shipping fee based on total price

    context = {
        'order': order,  # Pass the order object to the template
        'order_items': order_items,  # Pass order items to the template
        'shipping_fee': shipping_fee,
        'total_price': total_price + shipping_fee,  # Pass the total price including shipping fee
    }
    # Render the order confirmation page with the context data
    return render(request, 'order_confirmation.html', context)
