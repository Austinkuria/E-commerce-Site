from django.urls import path
from . import views 


urlpatterns = [
    path('', views.products_view, name='index'),
    path('index/', views.products_view, name='index'),
    path('login/', views.login_view, name='login'),
    path('signup/', views.signup_view, name='signup'),
    path('add_to_cart/', views.add_to_cart, name='add_to_cart'),
    path('remove_from_cart/', views.remove_from_cart, name='remove_from_cart'),
    path('update_cart/',views.update_cart, name='update_cart'),
    path('get_cart/', views.get_cart, name='get_cart'),
    path('is_logged_in/', views.is_logged_in, name='is_logged_in'),
    path('checkout_modal/', views.checkout_modal, name='checkout_modal'),
    path('checkout/', views.checkout, name='checkout'),
    path('order_confirmation/', views.order_confirmation, name='order_confirmation'),  path('shipping/', views.shipping_view, name='shipping'),
]
