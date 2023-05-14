from django.http import JsonResponse
from django.templatetags.static import static
from django.shortcuts import get_object_or_404
from django.db import transaction
from rest_framework.response import Response
from rest_framework.decorators import api_view

from geocoder.utils import create_address

from .models import Product, Order
from .serializers import OrderSerializer


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


@transaction.atomic
@api_view(['POST'])
def register_order(request):
    serializer = OrderSerializer(data=request.data)
    serializer.is_valid(raise_exception=True)
    order_details = serializer.validated_data

    order = Order.objects.create(
        firstname=order_details['firstname'],
        lastname=order_details['lastname'],
        phonenumber=order_details['phonenumber'],
        address=order_details['address']
    )
    create_address(order_details['address'])
    for product_detail in order_details['products']:
        product = get_object_or_404(Product, pk=product_detail['product'])
        order.products.create(
            product=product,
            quantity=product_detail['quantity'],
            price=product.price
        )
    return Response({
        'id': order.id,
        'firstname': order_details['firstname'],
        'lastname': order_details['lastname'],
        'phonenumber': order_details['phonenumber'],
        'address': order_details['address']
    })
