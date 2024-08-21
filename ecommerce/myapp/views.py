from django.contrib import messages
from django.shortcuts import render, get_object_or_404, redirect
from django.http import HttpResponseForbidden, JsonResponse, HttpResponseBadRequest
from django.views.decorators.csrf import csrf_protect
from django.contrib.auth.decorators import login_required
from .models import Product, Cart, CartItem, Order, OrderItem,ShippingDetails, Payment
from django.contrib.auth import authenticate, login, logout
from .models import Product, Profile
from django.contrib.auth.forms import UserCreationForm, AuthenticationForm
from .forms import CustomUserCreationForm, CustomLoginForm, UserUpdateForm, ProfileUpdateForm, CheckoutForm
from django.db import transaction
import logging

# Create your views here.


logger = logging.getLogger(__name__)

# Products View
def products_view(request):
    products = Product.objects.all()
    return render(request, 'index.html', {'products': products})

# Add to Cart View
@transaction.atomic
@login_required
@csrf_protect
def add_to_cart(request):
    if request.method == 'POST':
        product_id = request.POST.get('product_id')
        quantity = int(request.POST.get('quantity', 1))

        if not product_id:
            return HttpResponseBadRequest("Product ID is required")

        try:
            product = get_object_or_404(Product, id=product_id)
            if not product.is_in_stock():
                return JsonResponse({'status': 'error', 'message': 'Product is out of stock'}, status=400)

            cart, created = Cart.objects.get_or_create(user=request.user)
            cart.add_item(product, quantity)

            return JsonResponse({'status': 'success', 'message': 'Product added to cart'})
        except Exception as e:
            logger.error(f"Error adding product to cart: {e}")
            return JsonResponse({'status': 'error', 'message': str(e)}, status=500)

    return JsonResponse({'status': 'error', 'message': 'Invalid request method'}, status=400)

# Remove from Cart View
@login_required
@csrf_protect
def remove_from_cart(request):
    if request.method == 'POST':
        product_id = request.POST.get('product_id')
        if not product_id:
            return HttpResponseBadRequest("Product ID is required")

        try:
            product = Product.objects.get(id=product_id)
            cart = Cart.objects.get(user=request.user)
            cart_item = CartItem.objects.filter(cart=cart, product=product).first()
            if cart_item:
                cart_item.delete()
            return JsonResponse({'status': 'success'})
        except Product.DoesNotExist:
            return JsonResponse({'status': 'error', 'message': 'Product not found'}, status=404)
        except Cart.DoesNotExist:
            return JsonResponse({'status': 'error', 'message': 'Cart not found'}, status=404)
        except Exception as e:
            logger.error(f"Error removing product from cart: {e}")
            return JsonResponse({'status': 'error', 'message': str(e)}, status=500)

    return JsonResponse({'status': 'error'}, status=400)

# Update Cart View
@login_required
@csrf_protect
def update_cart(request):
    if request.method == 'POST':
        product_id = request.POST.get('product_id')
        action = request.POST.get('action')
        if not product_id or action not in ['increase', 'decrease']:
            return HttpResponseBadRequest("Invalid parameters")

        try:
            product = Product.objects.get(id=product_id)
            cart = Cart.objects.get(user=request.user)
            cart_item, created = CartItem.objects.get_or_create(cart=cart, product=product)
            if action == 'increase':
                cart_item.quantity += 1
            elif action == 'decrease' and cart_item.quantity > 1:
                cart_item.quantity -= 1
            cart_item.save()
            return JsonResponse({'status': 'success'})
        except Product.DoesNotExist:
            return JsonResponse({'status': 'error', 'message': 'Product not found'}, status=404)
        except Cart.DoesNotExist:
            return JsonResponse({'status': 'error', 'message': 'Cart not found'}, status=404)
        except Exception as e:
            logger.error(f"Error updating cart: {e}")
            return JsonResponse({'status': 'error', 'message': str(e)}, status=500)

    return JsonResponse({'status': 'error'}, status=400)

# Get Cart View
@login_required
@csrf_protect
def get_cart(request):
    try:
        cart = Cart.objects.get(user=request.user)
        cart_items = CartItem.objects.filter(cart=cart).select_related('product')

        items = []
        for item in cart_items:
            items.append({
                'id': item.id,
                'name': item.product.name,
                'price': item.product.price,
                'quantity': item.quantity
            })

        total = cart.get_total()

        return JsonResponse({'cart_items': items, 'total': total})
    except Cart.DoesNotExist:
        return JsonResponse({'cart_items': [], 'total': 0})

# Profile View

@login_required
@csrf_protect
def profile(request):
    # Ensure the user has a profile before proceeding
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

    context = {
        'user_form': user_form,
        'profile_form': profile_form
    }
    return render(request, 'users/profile.html', context)

@csrf_protect
def some_view(request):
    if request.user.is_authenticated:
        return redirect('checkout')
    else:
        request.session['next_page'] = request.path
        return redirect('login')

@csrf_protect
def signup_view(request):
    if request.method == 'POST':
        form = CustomUserCreationForm(request.POST)
        if form.is_valid():
            user = form.save()
            username = form.cleaned_data.get('username')
            password = form.cleaned_data.get('password1')
            user = authenticate(username=username, password=password)
            if user is not None:
                login(request, user)
                next_page = request.session.get('next_page', 'checkout')
                return redirect(next_page)
            else:
                form.add_error(None, "Authentication failed.")
    else:
        form = CustomUserCreationForm()
    return render(request, 'signup.html', {'form': form})

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
                next_page = request.session.get('next_page', 'home')  # Default to 'home' if not set
                request.session.pop('next_page', None)  # Clear session key after use
                return redirect(next_page)
    else:
        form = CustomLoginForm()
    return render(request, 'login.html', {'form': form})

# shipping fee calculation function 
def calculate_shipping_fee(order):
    total_price = order.calculate_total_price()  # returns the total price of the order
    if total_price < 50:
        return 10  # Flat fee for orders below $50
    elif total_price < 100:
        return 5   # Discounted fee for orders between $50 and $100
    else:
        return 0   # Free shipping for orders $100 and above

# Return whether the user is logged in or not
def is_logged_in(request):
    return JsonResponse({'is_authenticated': request.user.is_authenticated})

# Render the checkout when the user is logged in.
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
            Payment.objects.create(
                order=order,
                payment_method=payment_method,
                amount=order.total_price,
                transaction_id="N/A",  # Placeholder, not real transaction ID
                payment_status="pending"  # You can set this as 'pending' or other status
            )
            
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


    
# logout view
@csrf_protect
def logout_view(request):
    logger.debug(f"Request method: {request.method}")
    if request.method == 'POST':
        logout(request)
        return redirect('login')
    else:
        return HttpResponseForbidden("Only POST requests are allowed.")

@login_required
def place_order(request):
    if request.method == 'POST':
        form = CheckoutForm(request.POST)
        
        if form.is_valid():
            address = form.cleaned_data['address']
            city = form.cleaned_data['city']
            postal_code = form.cleaned_data['postal_code']
            
            # Assume cart data is stored in session
            cart = request.session.get('cart', {})
            
            if not cart or not cart.get('items'):
                return redirect('checkout')  # Redirect to checkout if the cart is empty
            
            # Calculate total price
            total = sum(item['price'] * item['quantity'] for item in cart['items'])
            
            # Create an order
            order = Order.objects.create(
                user=request.user,
                total=total,
                address=address,
                city=city,
                postal_code=postal_code
            )
            
            # Create order items
            for item in cart['items']:
                product = get_object_or_404(Product, id=item['product_id'])
                OrderItem.objects.create(
                    order=order,
                    product=product,
                    quantity=item['quantity'],
                    price=item['price']  # Ensure price is included if necessary
                )
            
            # Clear the cart
            request.session['cart'] = {}
            
            return redirect('order_confirmation')  # Redirect to order confirmation page
        else:
            # Handle form errors
            return render(request, 'checkout.html', {'form': form})
    
    # If the request method is not POST, redirect to checkout page
    return redirect('checkout')
# Create an order confirmation page that the user is redirected to after a successful checkout
@login_required
def order_confirmation(request):
    return render(request, 'order_confirmation.html')
