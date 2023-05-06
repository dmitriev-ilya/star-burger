from django.http import JsonResponse
from django.templatetags.static import static
from django.shortcuts import get_object_or_404
from rest_framework.response import Response
from rest_framework.decorators import api_view
from rest_framework import status
from phonenumber_field.phonenumber import PhoneNumber

from .models import Product
from .models import Order


def banners_list_api(request):
    # FIXME move data to db?
    return JsonResponse([
        {
            'title': 'Burger',
            'src': static('burger.jpg'),
            'text': 'Tasty Burger at your door step',
        },
        {
            'title': 'Spices',
            'src': static('food.jpg'),
            'text': 'All Cuisines',
        },
        {
            'title': 'New York',
            'src': static('tasty.jpg'),
            'text': 'Food is incomplete without a tasty dessert',
        }
    ], safe=False, json_dumps_params={
        'ensure_ascii': False,
        'indent': 4,
    })


def product_list_api(request):
    products = Product.objects.select_related('category').available()

    dumped_products = []
    for product in products:
        dumped_product = {
            'id': product.id,
            'name': product.name,
            'price': product.price,
            'special_status': product.special_status,
            'description': product.description,
            'category': {
                'id': product.category.id,
                'name': product.category.name,
            } if product.category else None,
            'image': product.image.url,
            'restaurant': {
                'id': product.id,
                'name': product.name,
            }
        }
        dumped_products.append(dumped_product)
    return JsonResponse(dumped_products, safe=False, json_dumps_params={
        'ensure_ascii': False,
        'indent': 4,
    })


@api_view(['POST'])
def register_order(request):
    try:
        order_details = request.data
        empty_fields = []
        if not order_details.get('products'):
            empty_fields.append('products')
        if not order_details.get('firstname'):
            empty_fields.append('firstname')
        if not order_details.get('address'):
            empty_fields.append('address')
        if not order_details.get('phonenumber'):
            empty_fields.append('phonenumber')
        if empty_fields:
            return Response(
                {'error': f'{", ".join(empty_fields)} can not be empty'},
                status=status.HTTP_451_UNAVAILABLE_FOR_LEGAL_REASONS
            )
        if not isinstance(order_details['products'], list) \
        or not isinstance(order_details['firstname'], str) \
        or not isinstance(order_details['address'], str):
            raise TypeError

        phonenumber = PhoneNumber.from_string(order_details.get('phonenumber'), region='RU')
        if not phonenumber.is_valid():
            return Response(
                {'error': 'not valid phonenumber'},
                status=status.HTTP_451_UNAVAILABLE_FOR_LEGAL_REASONS
            )
        order = Order.objects.create(
            firstname=order_details['firstname'],
            lastname=order_details.get('lastname', ''),
            phonenumber=phonenumber,
            address=order_details['address']
        )
        for product_detail in order_details['products']:
            product = get_object_or_404(Product, pk=product_detail['product'])
            order.products.create(
                product=product,
                quantity=product_detail['quantity']
            )
        return Response(order_details)

    except TypeError:
        return Response(
            {'error': 'check value type'},
            status=status.HTTP_451_UNAVAILABLE_FOR_LEGAL_REASONS
        )
