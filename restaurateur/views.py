from django import forms
from django.shortcuts import redirect, render
from django.views import View
from django.urls import reverse_lazy
from django.contrib.auth.decorators import user_passes_test

from django.contrib.auth import authenticate, login
from django.contrib.auth import views as auth_views

from foodcartapp.models import Product, Restaurant, Order, RestaurantMenuItem
from geocoder.models import Address
from geocoder.utils import calculate_distance


class Login(forms.Form):
    username = forms.CharField(
        label='Логин', max_length=75, required=True,
        widget=forms.TextInput(attrs={
            'class': 'form-control',
            'placeholder': 'Укажите имя пользователя'
        })
    )
    password = forms.CharField(
        label='Пароль', max_length=75, required=True,
        widget=forms.PasswordInput(attrs={
            'class': 'form-control',
            'placeholder': 'Введите пароль'
        })
    )


class LoginView(View):
    def get(self, request, *args, **kwargs):
        form = Login()
        return render(request, "login.html", context={
            'form': form
        })

    def post(self, request):
        form = Login(request.POST)

        if form.is_valid():
            username = form.cleaned_data['username']
            password = form.cleaned_data['password']

            user = authenticate(request, username=username, password=password)
            if user:
                login(request, user)
                if user.is_staff:  # FIXME replace with specific permission
                    return redirect("restaurateur:RestaurantView")
                return redirect("start_page")

        return render(request, "login.html", context={
            'form': form,
            'ivalid': True,
        })


class LogoutView(auth_views.LogoutView):
    next_page = reverse_lazy('restaurateur:login')


def is_manager(user):
    return user.is_staff  # FIXME replace with specific permission


@user_passes_test(is_manager, login_url='restaurateur:login')
def view_products(request):
    restaurants = list(Restaurant.objects.order_by('name'))
    products = list(Product.objects.prefetch_related('menu_items'))

    products_with_restaurant_availability = []
    for product in products:
        availability = {item.restaurant_id: item.availability for item in product.menu_items.all()}
        ordered_availability = [availability.get(restaurant.id, False) for restaurant in restaurants]

        products_with_restaurant_availability.append(
            (product, ordered_availability)
        )

    return render(request, template_name="products_list.html", context={
        'products_with_restaurant_availability': products_with_restaurant_availability,
        'restaurants': restaurants,
    })


@user_passes_test(is_manager, login_url='restaurateur:login')
def view_restaurants(request):
    return render(request, template_name="restaurants_list.html", context={
        'restaurants': Restaurant.objects.all(),
    })


@user_passes_test(is_manager, login_url='restaurateur:login')
def view_orders(request):
    orders = Order.objects.exclude(status='В').prefetch_related('products').select_related('restaurant').total_price()
    order_items = []
    product_with_availability = RestaurantMenuItem.objects.filter(availability=True).select_related('restaurant', 'product')
    for order in orders:
        products_in_order = order.products.all().values_list('product')
        avaliable_restaurants = set(
            [item.restaurant for item in product_with_availability.filter(product_id__in=products_in_order)]
        )

        avaliable_restaurants_with_distance = []
        order_address = Address.objects.get(address=order.address)
        for restaurant in avaliable_restaurants:
            restaurant_name = restaurant.name
            restaurant_address = Address.objects.get(address=restaurant.address)
            distance_to_order = calculate_distance(order_address, restaurant_address)
            avaliable_restaurants_with_distance.append((restaurant_name, distance_to_order))

        order_details = {
            'id': order.id,
            'total_price': order.total_price,
            'client': f'{order.firstname} {order.lastname}',
            'phonenumber': order.phonenumber,
            'address': order.address,
            'status': order.get_status_display(),
            'comment': order.comment,
            'payment_method': order.get_payment_method_display(),
            'avaliable_restaurants': sorted(
                avaliable_restaurants_with_distance,
                key=lambda restaurant: restaurant[1]
            ),
            'cooking_in': order.restaurant
        }
        order_items.append(order_details)

    context = {
        'order_items': order_items
    }

    return render(request, template_name='order_items.html', context=context)
