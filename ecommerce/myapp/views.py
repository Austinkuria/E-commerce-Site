from django.shortcuts import render, get_object_or_404, redirect
from django.http import JsonResponse
from django.views.decorators.csrf import csrf_exempt
from django.contrib.auth.decorators import login_required
from .models import Product, Cart, CartItem
from django.shortcuts import render, redirect
from django.contrib.auth import authenticate, login
from .forms import CustomAuthenticationForm,CustomUserCreationForm

# Create your views here.

def products_view(request):
    products = Product.objects.all()
    return render(request, 'index.html', {'products': products})

@login_required
@csrf_exempt
def add_to_cart(request):
    if request.method == 'POST':
        product_id = request.POST.get('product_id')
        product = get_object_or_404(Product, id=product_id)
        cart, created = Cart.objects.get_or_create(user=request.user)
        cart_item, created = CartItem.objects.get_or_create(cart=cart, product=product)
        if not created:
            cart_item.quantity += 1
            cart_item.save()
        return JsonResponse({'status': 'success'})
    return JsonResponse({'status': 'error'})

@login_required
@csrf_exempt
def remove_from_cart(request):
    if request.method == 'POST':
        product_id = request.POST.get('product_id')
        product = get_object_or_404(Product, id=product_id)
        cart = get_object_or_404(Cart, user=request.user)
        CartItem.objects.filter(cart=cart, product=product).delete()
        return JsonResponse({'status': 'success'})
    return JsonResponse({'status': 'error'})

@login_required
@csrf_exempt
def update_cart(request):
    if request.method == 'POST':
        product_id = request.POST.get('product_id')
        action = request.POST.get('action')
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
    cart = get_object_or_404(Cart, user=request.user)
    cart_items = cart.items.all()
    items = [{'id': item.product.id, 'name': item.product.name, 'price': item.product.price, 'quantity': item.quantity} for item in cart_items]
    return JsonResponse({'cart_items': items})

def signup_view(request):
    if request.method == 'POST':
        form = CustomUserCreationForm(request.POST)
        if form.is_valid():
            user = form.save()
            login(request, user)
            return redirect('home')  # Redirect after successful signup
    else:
        form = CustomUserCreationForm()
    return render(request, 'signup.html', {'form': form})

def login_view(request):
    if request.method == 'POST':
        form = CustomAuthenticationForm(request, data=request.POST)
        if form.is_valid():
            user = form.get_user()
            login(request, user)
            return redirect('home')  # Redirect after successful login
    else:
        form = CustomAuthenticationForm()
    return render(request, 'login.html', {'form': form})