from django.shortcuts import get_object_or_404
from rest_framework.serializers import ModelSerializer
from rest_framework.fields import IntegerField

from .models import Order, OrderProduct, Product


class OrderProductSerializer(ModelSerializer):
    product = IntegerField()

    class Meta:
        model = OrderProduct
        fields = ['product', 'quantity']


class OrderSerializer(ModelSerializer):
    products = OrderProductSerializer(many=True, allow_empty=False)

    def create(self, validated_data):
        order = Order.objects.create(
            firstname=validated_data['firstname'],
            lastname=validated_data['lastname'],
            phonenumber=validated_data['phonenumber'],
            address=validated_data['address']
        )
        for product_detail in validated_data['products']:
            product = get_object_or_404(Product, pk=product_detail['product'])
            order.products.create(
                product=product,
                quantity=product_detail['quantity'],
                price=product.price
            )
        return order

    class Meta:
        model = Order
        fields = ['firstname', 'lastname', 'phonenumber', 'address', 'products']
