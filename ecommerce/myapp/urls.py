from django.urls import path
from . import views 


urlpatterns = [
    path('', views.products_view, name='index'),
    path('index/', views.products_view, name='index'),
    path('profile/', views.profile, name='profile'),
    path('login/', views.login_view, name='login'),
    path('signup/', views.signup_view, name='signup'),
<<<<<<< HEAD
    path('logout/', LogoutView.as_view(next_page='login'), name='logout'),
=======
    path('logout/', views.logout_view, name='logout'),
>>>>>>> 78f4d44396c0843fd4210fce5a99e9df41c2f089
    path('some-page/', views.some_view, name='some_view'),
    path('add_to_cart/', views.add_to_cart, name='add_to_cart'),
    path('remove_from_cart/', views.remove_from_cart, name='remove_from_cart'),
    path('update_cart/', views.update_cart, name='update_cart'),
    path('get_cart/', views.get_cart, name='get_cart'),
    path('is_logged_in/', views.is_logged_in, name='is_logged_in'),
    path('place_order/', views.place_order, name='place_order'),
    path('checkout/', views.checkout_view, name='checkout'),
    path('order_confirmation/', views.order_confirmation, name='order_confirmation'),
]
