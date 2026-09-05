from django.shortcuts import render, redirect
from .models import Product, CartItem, CustomerProfile, Order, OrderItem
from django.http import JsonResponse
from django.template.loader import render_to_string
from django.shortcuts import render, redirect, get_object_or_404
from django.contrib.auth.decorators import login_required
from django.contrib.auth.models import User
from django.contrib.auth import authenticate, login as auth_login
from django.http import JsonResponse
from django.template.loader import render_to_string
from django.contrib.auth import logout
import stripe
from django.conf import settings
from django.db.models import Q




stripe.api_key = settings.STRIPE_SECRET_KEY


# Create your views here.
def homepage(request):
    return render(request, "homepage.html")

def electronics(request):
    products = Product.objects.filter(category="Electronics")
    return render(request, "electronics.html", {'products': products} )

def clothing(request):
    products = Product.objects.filter(category="Clothing")
    return render(request, "clothing.html", {'products': products})

def accessories(request):
    products = Product. objects.filter(category="Accessories")
    return render(request, "accessories.html", {'products': products} )

def mobiles(request):

    products = Product.objects.filter(category="Mobile")
    return render( request, "mobiles.html", { "products": products })

def laptops(request):

    products = Product.objects.filter(category="Laptop")
    return render ( request, "laptops.html", { "products": products })

def navbar(request):
    return render(request, "navbar.html")

def login(request):

    if request.method == "POST":

        login_id = request.POST.get("login_id")
        password = request.POST.get("password")

        user = None

        user_by_email = User.objects.filter(email=login_id).first()

        if user_by_email:
            user = authenticate(
                request,
                username=user_by_email.username,
                password=password
            )
        else:
            profile = CustomerProfile.objects.filter(
                phone_number=login_id
            ).select_related("user").first()

            if profile:
                user = authenticate(
                    request,
                    username=profile.user.username,
                    password=password
                )

        if user is not None:
            auth_login(request, user)

            next_url = request.POST.get("next")

            if next_url:
                return redirect(next_url)

            return redirect("homepage")

        return render(request, "login.html", {
            "error": "Invalid email/phone number or password."
        })

    return render(request, "login.html")


def register(request):

    if request.method == "POST":

        name = request.POST.get("name")
        email = request.POST.get("email")
        phone_number = request.POST.get("phone_number")
        password = request.POST.get("password")

        if User.objects.filter(email=email).exists():
            return render(request, "register.html", {
                "error": "Email already exists."
            })

        user = User.objects.create_user(
            username=email,
            email=email,
            password=password,
            first_name=name
        )

        CustomerProfile.objects.create(
            user=user,
            phone_number=phone_number
        )

        return redirect("login")

    return render(request, "register.html")

@login_required(login_url='login')
def add_to_cart(request, product_id):
    product = get_object_or_404(Product, id=product_id)

    try:
        quantity = int(request.POST.get('quantity', 1))
    except (ValueError, TypeError):
        quantity = 1

    quantity = max(quantity, 1)

    cart_item, created = CartItem.objects.get_or_create(
        user=request.user,
        product=product
    )

    if created:
        cart_item.quantity = quantity
    else:
        cart_item.quantity += quantity

    cart_item.save()

    if request.headers.get('x-requested-with') == 'XMLHttpRequest':
        return get_cart_panel_response(request)

    return redirect('cart')




@login_required(login_url='login')
def cart(request):
    products = CartItem.objects.filter(user=request.user)
    total = sum(item.subtotal() for item in products)

    return render(request, "cart.html", {
        "products": products,
        "total": total
    })




def cart_panel(request):
    return get_cart_panel_response(request)




def get_cart_panel_response(request):
    products = CartItem.objects.filter(user=request.user)
    total = sum(item.subtotal() for item in products)
    count = sum(item.quantity for item in products)

    html = render_to_string("cart_panel.html", {"products": products, "total": total}, request=request)

    return JsonResponse({"html": html, "count": count})




def remove_from_cart(request, item_id):
    cart_item = get_object_or_404( CartItem, id=item_id, user=request.user )
    cart_item.delete()

    if request.headers.get('x-requested-with') == 'XMLHttpRequest':
        return get_cart_panel_response(request)

    return redirect('cart')






@login_required(login_url='login')
def buy_now(request, product_id):
    product = get_object_or_404(Product, id=product_id)

    try:
        quantity = int(request.POST.get('quantity', 1))
    except (ValueError, TypeError):
        quantity = 1

    quantity = max(quantity, 1)

    cart_item, created = CartItem.objects.get_or_create(
        user=request.user,
        product=product
    )

    if created:
        cart_item.quantity = quantity
    else:
        cart_item.quantity += quantity

    cart_item.save()

    return redirect('checkout')



def logout_view(request):
    logout(request)
    return redirect('homepage')


@login_required(login_url='login')
def checkout(request):

    cart_items = CartItem.objects.filter(user=request.user)

    if not cart_items.exists():
        return redirect('cart')

    total = sum(
        item.product.price * item.quantity
        for item in cart_items
    )

    if request.method == "POST":

        full_name = request.POST.get('name')
        email = request.POST.get('email')
        phone = request.POST.get('phone')
        address = request.POST.get('address')
        city = request.POST.get('city')
        postal_code = request.POST.get('postal_code')

        payment_method = request.POST.get('payment_method')

        order = Order.objects.create(
            user=request.user,
            full_name=full_name,
            email=email,
            phone=phone,
            address=address,
            city=city,
            postal_code=postal_code,
            total=total,
            status="pending",
            payment_method=payment_method
        )

        for item in cart_items:

            OrderItem.objects.create(
                order=order,
                product=item.product,
                quantity=item.quantity,
                price=item.product.price
            )

        # Cash on Delivery
        if payment_method == "cod":

            cart_items.delete()

            return redirect('order_success', order_id=order.id)

        # Stripe
        return redirect('start_payment', order_id=order.id)

    return render(request, 'checkout.html', {
        'cart_items': cart_items,
        'total': total,
    })



@login_required(login_url='login')
def start_payment(request, order_id):

    order = get_object_or_404(
        Order,
        id=order_id,
        user=request.user
    )

    checkout_session = stripe.checkout.Session.create(
        payment_method_types=['card'],

        line_items=[
            {
                'price_data': {
                    'currency': 'pkr',
                    'product_data': {
                        'name': f'Order #{order.id}',
                    },
                    'unit_amount': int(order.total * 100),
                },
                'quantity': 1,
            }
        ],

        mode='payment',

        success_url=request.build_absolute_uri(
            '/payment/success/'
        ) + f'?session_id={{CHECKOUT_SESSION_ID}}',

        cancel_url=request.build_absolute_uri(
            '/payment/cancel/'
        ),

        metadata={
            'order_id': str(order.id),
        }
    )

    order.stripe_session_id = checkout_session.id
    order.save()

    return redirect(checkout_session.url)

@login_required(login_url='login')
def payment_success(request):

    session_id = request.GET.get('session_id')

    session = stripe.checkout.Session.retrieve(session_id)

    order_id = session.metadata.order_id

    order = get_object_or_404(
        Order,
        id=order_id,
        user=request.user
    )

    if session.payment_status == 'paid':
        order.status = 'paid'
        order.payment_id = session.payment_intent
        order.save()

        CartItem.objects.filter(user=request.user).delete()

    return render(request, 'payment_success.html', {
        'order': order
    })


@login_required(login_url='login')
def payment_cancel(request):

    return render(request, 'payment_cancel.html')



@login_required(login_url='login')
def order_success(request, order_id):
    order = Order.objects.get(
        id=order_id,
        user=request.user
    )

    return render(request, 'order_success.html', {
        'order': order
    })






def product_detail(request, product_id):
    product = get_object_or_404(Product, id=product_id)

    return render(request, 'product_detail.html', {
        'product': product
    })



def search_products(request):
    query = request.GET.get('q', '').strip()

    products = Product.objects.none()

    if query:
        products = Product.objects.filter(
            Q(name__icontains=query) |
            Q(description__icontains=query) |
            Q(category__icontains=query)
        )

    return render(request, 'search.html', {
        'products': products,
        'query': query,
    })