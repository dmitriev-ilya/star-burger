from rest_framework.serializers import ModelSerializer
from rest_framework.fields import IntegerField

from .models import Order, OrderProduct


class OrderProductSerializer(ModelSerializer):
    product = IntegerField()

    class Meta:
        model = OrderProduct
        fields = ['product', 'quantity']


class OrderSerializer(ModelSerializer):
    products = OrderProductSerializer(many=True, allow_empty=False)

    class Meta:
        model = Order
        fields = ['firstname', 'phonenumber', 'address', 'products']
