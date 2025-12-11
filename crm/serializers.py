from rest_framework import serializers
from .models import Customer, Product, Order


class CustomerSerializer(serializers.ModelSerializer):
    class Meta:
        model = Customer
        field = "__all__"


class ProductSerializer(serializers.ModelSerializer):
    class Meta:
        model = Product
        field = "__all__"


class OrderSerializer(serializers.ModelSerializer):
    customer = CustomerSerializer()
    products = ProductSerializer(many=True)

    class Meta:
        model = Order
        field = "__all__"
