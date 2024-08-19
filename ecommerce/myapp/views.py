from pyexpat.errors import messages
from django.shortcuts import render, get_object_or_404, redirect
from django.http import JsonResponse, HttpResponseBadRequest
from django.views.decorators.csrf import csrf_protect
from django.contrib.auth.decorators import login_required
from .models import Product, Cart, CartItem, Order, OrderItem
from django.contrib.auth import authenticate, login
from django.contrib.auth.forms import UserCreationForm, AuthenticationForm
from .forms import CustomUserCreationForm, CustomLoginForm, CheckoutForm
# Create your views here.

def products_view(request):
    products = Product.objects.all()
    return render(request, 'index.html', {'products': products})

@login_required
@csrf_protect
def add_to_cart(request):
    if request.method == 'POST':
        product_id = request.POST.get('product_id')
        quantity = int(request.POST.get('quantity', 1))  # Default to 1 if quantity is not provided

        if not product_id:
            return HttpResponseBadRequest("Product ID is required")

        try:
            product = get_object_or_404(Product, id=product_id)
            cart, created = Cart.objects.get_or_create(user=request.user)
            cart_item, created = CartItem.objects.get_or_create(cart=cart, product=product)
            cart_item.quantity += quantity
            cart_item.save()

            return JsonResponse({'status': 'success', 'message': 'Product added to cart'})
        except Exception as e:
            return JsonResponse({'status': 'error', 'message': str(e)}, status=500)

    return JsonResponse({'status': 'error', 'message': 'Invalid request method'}, status=400)


@login_required
@csrf_protect
def remove_from_cart(request):
    if request.method == 'POST':
        product_id = request.POST.get('product_id')
        if not product_id:
            return HttpResponseBadRequest("Product ID is required")
        product = get_object_or_404(Product, id=product_id)
        cart = get_object_or_404(Cart, user=request.user)
        cart_item = CartItem.objects.filter(cart=cart, product=product).first()
        if cart_item:
            cart_item.delete()
        return JsonResponse({'status': 'success'})
    return JsonResponse({'status': 'error'})

@login_required
@csrf_protect
def update_cart(request):
    if request.method == 'POST':
        product_id = request.POST.get('product_id')
        action = request.POST.get('action')
        if not product_id or action not in ['increase', 'decrease']:
            return HttpResponseBadRequest("Invalid parameters")

        product = get_object_or_404(Product, id=product_id)
        cart = get_object_or_404(Cart, user=request.user)
        cart_item, created = CartItem.objects.get_or_create(cart=cart, product=product)
        if action == 'increase':
            cart_item.quantity += 1
        elif action == 'decrease' and cart_item.quantity > 1:
            cart_item.quantity -= 1
        cart_item.save()
        return JsonResponse({'status': 'success'})
    return JsonResponse({'status': 'error'})

@login_required
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

        return JsonResponse({'cart_items': items})
    except Cart.DoesNotExist:
        return JsonResponse({'cart_items': []})
    except Exception as e:
        return JsonResponse({'error': str(e)}, status=500)

def signup_view(request):
    if request.method == 'POST':
        form = CustomUserCreationForm(request.POST)
        if form.is_valid():
            user = form.save()
            username = form.cleaned_data.get('username')
            password = form.cleaned_data.get('password')
            user = authenticate(username=username, password=password)
            login(request, user)
            return redirect('checkout')  # Redirect to the shipping details form after signup
    else:
        form = CustomUserCreationForm()
    return render(request, 'signup.html', {'form': form})

def login_view(request):
    if request.method == 'POST':
        form = CustomLoginForm(request, data=request.POST)
        if form.is_valid():
            username = form.cleaned_data.get('username')
            password = form.cleaned_data.get('password')
            user = authenticate(username=username, password=password)
            if user is not None:
                login(request, user)
                return redirect('some_next_page')  # Redirect to the page after login
    else:
        form = CustomLoginForm()
    return render(request, 'login.html', {'form': form})

# Return whether the user is logged in or not
def is_logged_in(request):
    return JsonResponse({'is_authenticated': request.user.is_authenticated})

# Render the checkout when the user is logged in.
@login_required
@csrf_protect
def checkout_view(request):
    cart = Cart.objects.get(user=request.user)
    cart_items = CartItem.objects.filter(cart=cart)

    if not cart_items.exists():
        messages.warning(request, "Your cart is empty.")
        return redirect('cart')

    total = sum(item.get_total_price() for item in cart_items)

    if request.method == 'POST':
        form = CheckoutForm(request.POST)
        if form.is_valid():
            # Save order and order details here
            # Clear the cart after successful checkout
            cart_items.delete()
            messages.success(request, "Order placed successfully!")
            return redirect('order_confirmation')
    else:
        form = CheckoutForm()

    return render(request, 'checkout.html', {
        'form': form,
        'cart_items': cart_items,
        'total': total
    })

@login_required
def place_order(request):
    if request.method == 'POST':
        address = request.POST.get('address')
        city = request.POST.get('city')
        postal_code = request.POST.get('postal_code')
        
        # Assume cart data is stored in session
        cart = request.session.get('cart', {})
        
        if not cart or not cart.get('items'):
            return redirect('checkout')  # Redirect to the checkout page if the cart is empty
        
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
            product = Product.objects.get(id=item['product_id'])
            OrderItem.objects.create(
                order=order,
                product=product,
                quantity=item['quantity']
            )
        
        # Clear the cart
        request.session['cart'] = {}
        
        return redirect('order_confirmation')  # Redirect to order confirmation page
    
    # If the request method is not POST, redirect to the checkout page
    return redirect('checkout')
# Create an order confirmation page that the user is redirected to after a successful checkout
@login_required
def order_confirmation(request):
    return render(request, 'order_confirmation.html')
