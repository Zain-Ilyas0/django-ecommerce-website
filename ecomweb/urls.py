from django.urls import path
from . import views



urlpatterns = [
    path('', views.homepage, name="homepage"),
    path('navbar/', views.navbar),
    path('electronics/', views.electronics, name="electronics"),
    path('clothing/', views.clothing, name="clothing"),
    path('accessories/', views.accessories, name="accessories"),
    path('mobiles/', views.mobiles, name="mobiles"),
    path('laptops/', views.laptops, name="laptops"),
    path('login/', views.login, name="login"),
    path('register/', views.register, name="register"),
    path('cart/', views.cart, name='cart'),
    path('cart/panel/', views.cart_panel, name='cart_panel'),   # ADD THIS LINE
    path('add-to-cart/<int:product_id>/', views.add_to_cart, name='add_to_cart'),
    path('remove-from-cart/<int:item_id>/', views.remove_from_cart, name='remove_from_cart'),
    path('buy-now/<int:product_id>/', views.buy_now, name='buy_now'),
    path('logout/', views.logout_view, name="logout"),
    path('checkout/', views.checkout, name="checkout"),
    path('payment/<int:order_id>/', views.start_payment, name='start_payment' ),
    path('payment/success/', views.payment_success, name='payment_success' ),
    path('payment/cancel/', views.payment_cancel, name='payment_cancel' ),
    path('order-success/<int:order_id>/', views.order_success, name='order_success'),
    path('product/<int:product_id>/', views.product_detail, name='product_detail' ),
    path('search/', views.search_products, name='search'),
]


