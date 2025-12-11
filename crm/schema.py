import graphene
from graphene import relay, Mutation, Field, List, ObjectType
from django.db import transaction
from django.utils import timezone
from graphene_django import DjangoObjectType
from graphene_django.filter import DjangoFilterConnectionField
from graphene_django.rest_framework.mutation import SerializerMutation

from .filters import CustomerFilter, ProductFilter, OrderFilter

from .models import Product, Order, Customer
from .serializers import ProductSerializer, OrderSerializer, CustomerSerializer

import re


def validate_phone(phone: str):
    if not phone:
        return True
    pattern = r"^\+?\d[\d\-]{7,}$"
    return re.match(pattern, phone) is not None


class ProductType(DjangoObjectType):

    class Meta:
        model = Product
        filterset_class = ProductFilter
        interfaces = (relay.Node,)


class CustomerType(DjangoObjectType):

    class Meta:
        model = Customer
        filterset_class = CustomerFilter
        interfaces = (relay.Node,)


class OrderType(DjangoObjectType):

    class Meta:
        model = Order
        filterset_class = OrderFilter
        interfaces = (relay.Node,)


class Query(graphene.ObjectType):
    customer = relay.Node.Field(CustomerType)
    all_customers = DjangoFilterConnectionField(CustomerType)

    product = relay.Node.Field(ProductType)
    all_products = DjangoFilterConnectionField(ProductType)

    order = relay.Node.Field(OrderType)
    all_orders = DjangoFilterConnectionField(OrderType)


class CreateCustomer(graphene.Mutation):
    class Arguments:
        name = graphene.String(required=True)
        email = graphene.String(required=True)
        phone = graphene.String(required=False)

    customer = graphene.Field(CustomerType)
    message = graphene.String()

    @staticmethod
    def mutate(root, info, name, email, phone=None):

        # Unique email check
        if Customer.objects.filter(email=email).exists():
            raise Exception("Email already exists")

        # Validate phone number
        if not validate_phone(phone):
            raise Exception("Invalid phone format")

        customer = Customer.objects.create(name=name, email=email, phone=phone)

        return CreateCustomer(
            customer=customer, message="Customer created successfully."
        )


class BulkCreateCustomers(graphene.Mutation):
    class Arguments:
        customers = List(
            graphene.JSONString,
            required=True,
        )

    created = graphene.List(CustomerType)
    errors = List(graphene.String)

    @staticmethod
    @transaction.atomic
    def mutate(root, info, customers):

        created_list = []
        error_list = []

        for entry in customers:
            name = entry.get("name")
            email = entry.get("email")
            phone = entry.get("phone")

            if not name or not email:
                error_list.append(f"Missing required fields for entry: {entry}")
                continue

            if Customer.objects.filter(email=email).exists():
                error_list.append(f"Duplicate email: {email}")
                continue

            if not validate_phone(phone):
                error_list.append(f"Invalid phone format for: {phone}")
                continue

            customer = Customer.objects.create(name=name, email=email, phone=phone)
            created_list.append(customer)

        return BulkCreateCustomers(created=created_list, errors=error_list)


class CreateProduct(graphene.Mutation):
    class Arguments:
        name = graphene.String(required=True)
        price = graphene.Float(required=True)
        stock = graphene.Int(required=False)

    product = graphene.Field(ProductType)
    message = graphene.String()

    @staticmethod
    def mutate(root, info, name, price, stock=0):

        if price <= 0:
            raise Exception("Price must be positive")

        if stock < 0:
            raise Exception("Stock cannot be negative")

        product = Product.objects.create(name=name, price=price, stock=stock)

        return CreateProduct(product=product, message="Product created successfully.")


class CreateOrder(graphene.Mutation):
    class Arguments:
        customer_id = graphene.ID(required=True)
        product_ids = List(graphene.ID, required=True)
        order_date = graphene.DateTime(required=False)

    order = graphene.Field(OrderType)
    message = graphene.String()

    @staticmethod
    def mutate(root, info, customer_id, product_ids, order_date=None):

        # Validate customer
        try:
            customer = Customer.objects.get(id=customer_id)
        except Customer.DoesNotExist:
            raise Exception("Invalid customer ID")

        if not product_ids:
            raise Exception("At least one product must be selected")

        # Validate products
        products = Product.objects.filter(id__in=product_ids)
        if len(products) != len(product_ids):
            raise Exception("One or more invalid product IDs")

        # Create order
        order = Order.objects.create(
            customer=customer, order_date=order_date or timezone.now()
        )
        order.products.set(products)

        # Calculate total amount
        total = sum(p.price for p in products)
        order.total_amount = total
        order.save()

        return CreateOrder(order=order, message="Order created successfully.")


class Mutation(graphene.ObjectType):
    create_customer = CreateCustomer.Field()
    bulk_create_customers = BulkCreateCustomers.Field()
    create_product = CreateProduct.Field()
    create_order = CreateOrder.Field
