from django.urls import path
from .views import add_to_cart, remove_from_cart, update_cart, get_cart
from .views import login_view, signup_view,products_view


urlpatterns = [
    path('', products_view, name='index'),
    path('index/', products_view, name='index'),
    path('login/', login_view, name='login'),
    path('signup/', signup_view, name='signup'),
    path('add_to_cart/', add_to_cart, name='add_to_cart'),
    path('remove_from_cart/', remove_from_cart, name='remove_from_cart'),
    path('update_cart/', update_cart, name='update_cart'),
    path('get_cart/', get_cart, name='get_cart'),
]
