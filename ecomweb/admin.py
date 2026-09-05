from django.contrib import admin
from .models import Product, CartItem, Order, OrderItem, CustomerProfile


@admin.register(Product)
class ProductAdmin(admin.ModelAdmin):

    list_display = (
        'id',
        'name',
        'category',
        'price',
    )

    list_filter = (
        'category',
    )

    search_fields = (
        'name',
        'category',
    )


@admin.register(CartItem)
class CartItemAdmin(admin.ModelAdmin):

    list_display = (
        'id',
        'product',
        'quantity',
    )

    list_filter = (
        'product',
    )

    search_fields = (
        'product__name',
    )

@admin.register(Order)
class OrderAdmin(admin.ModelAdmin):

    list_display = (
        'id',
        'user',
        'full_name',
        'email',
        'phone',
        'total',
        'status',
        'created_at',
    )

    list_filter = (
        'status',
        'city',
        'created_at',
    )

    search_fields = (
        'full_name',
        'email',
        'phone',
        'user__username',
    )

@admin.register(OrderItem)
class OrderItemAdmin(admin.ModelAdmin):

    list_display = (
        'id',
        'order',
        'product',
        'quantity',
        'price',
    )

    list_filter = (
        'product',
    )

    search_fields = (
        'product__name',
    )


@admin.register(CustomerProfile)
class CustomerProfileAdmin(admin.ModelAdmin):

    list_display = (
        'id',
        'get_name',
        'user',
        'phone_number',
    )

    search_fields = (
        'user__first_name',
        'user__email',
        'phone_number',
    )

    def get_name(self, obj):
        return obj.user.first_name

    get_name.short_description = 'Name'