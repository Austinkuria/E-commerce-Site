from django.shortcuts import render, get_object_or_404, redirect
from django.http import JsonResponse, HttpResponseBadRequest
from django.views.decorators.csrf import csrf_protect
from django.contrib.auth.decorators import login_required
from .models import Product, Cart, CartItem
from django.contrib.auth import authenticate, login
from django.contrib.auth.forms import UserCreationForm
from .forms import CustomUserCreationForm, ShippingDetailsForm
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
        cart = get_object_or_404(Cart, user=request.user)
        cart_items = cart.items.all()
        items = [
            {     
                'id': item.product.id, 
                'name': item.product.name, 
                'price': item.product.price,
                'quantity': item.quantity
            }
            for item in cart_items
        ]
        return JsonResponse({'cart_items': items})
    except Exception as e:
        return JsonResponse({'error': str(e)}, status=500)


def signup_view(request):
    if request.method == 'POST':
        form = CustomUserCreationForm(request.POST)
        if form.is_valid():
            user = form.save()
            username = form.cleaned_data.get('username')
            password = form.cleaned_data.get('password1')
            user = authenticate(username=username, password=password)
            login(request, user)
            return redirect('shipping')  # Redirect to the shipping details form after signup
    else:
        form = CustomUserCreationForm()
    return render(request, 'signup.html', {'form': form})
def login_view(request):
    if request.method == 'POST':
        form = CustomAuthenticationForm(request, data=request.POST)
        if form.is_valid():
            user = form.get_user()
            login(request, user)
            return redirect('index')  # Redirect after successful login
    else:
        form = CustomAuthenticationForm()
    return render(request, 'login.html', {'form': form})

# Return whether the user is logged in or not
def is_logged_in(request):
    return JsonResponse({'is_authenticated': request.user.is_authenticated})

# Render the checkout modal when the user is logged in.
@login_required
def checkout_modal(request):
    return render(request, 'checkout_modal.html')

# Process the order when the user submits the form.
@login_required
def checkout(request):
    if request.method == 'POST':
        
        shipping_address = request.POST.get('shipping_address')

        # Process the order...

        return redirect('order_confirmation')  # Redirect to an order confirmation page

    return redirect('home')  # Redirect to home if the request method is not POST

# Create an order confirmation page that the user is redirected to after a successful checkout
@login_required
def order_confirmation(request):
    return render(request, 'order_confirmation.html')
@login_required
def shipping_view(request):
    if request.method == 'POST':
        form = ShippingDetailsForm(request.POST)
        if form.is_valid():
            shipping_details = form.save(commit=False)
            shipping_details.user = request.user
            shipping_details.save()
            return redirect('some_next_page')
    else:
        form = ShippingDetailsForm()
    return render(request, 'shipping.html', {'form': form})