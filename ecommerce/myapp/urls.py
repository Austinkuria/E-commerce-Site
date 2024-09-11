from django.urls import path
from . import views

urlpatterns = [
    path('', views.products_view, name='index'),
    path('index/', views.products_view, name='index'),
    path('accounts/profile/', views.profile, name='profile'),
    path('accounts/login/', views.login_view, name='login'),
    path('accounts/signup/', views.signup_view, name='signup'),
    path('log_out/', views.log_out, name='log_out'),
    path('some-page/', views.some_view, name='some_view'),
    path('add_to_cart/', views.add_to_cart, name='add_to_cart'),
    path('remove_from_cart/', views.remove_from_cart, name='remove_from_cart'),
    path('update_cart/', views.update_cart, name='update_cart'),
    path('get_cart/', views.get_cart, name='get_cart'),
    path('is_logged_in/', views.is_logged_in, name='is_logged_in'),
    path('place_order/', views.place_order, name='place_order'),
    path('checkout/', views.checkout_view, name='checkout'),
    path('order_confirmation/<int:order_id>/', views.order_confirmation_view, name='order_confirmation'),  # Maps 'order_confirmation/<int:order_id>/' URL to 'order_confirmation_view' and expects an integer 'order_id'
    path('about-us/', views.about_us, name='about_us'),
    path('contact/', views.contact, name='contact'),
    path('privacy-policy/', views.privacy_policy, name='privacy_policy'),
    path('terms-of-service/', views.terms_of_service, name='terms_of_service'),
    path('shipping-information/', views.shipping_information, name='shipping_information'),
    path('returns-exchanges/', views.returns_exchanges, name='returns_exchanges'),
    path('faq/', views.faq, name='faq'),
    path('track-order/', views.track_order_view, name='track_order'),
]
