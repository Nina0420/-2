
from rest_framework import serializers
from rest_framework.serializers import ModelSerializer, StringRelatedField, IntegerField, DecimalField
from backend.models import (Category, Order,  OrderItem, Product, ProductInfo, ProductParameter, Shop, User, ClientCard,
                            Parameter )
from .models import ProductInfo, BasketItem

class ClientCardSerializer(ModelSerializer):

    class Meta:
        model = ClientCard
        fields = ('id', 'city', 'street', 'buildings', 'apt', 'user', 'mobile')
        read_only_fields = ('id',)
        extra_kwargs = {
            'user': {'write_only': True}
        }
class CategorySerializer(ModelSerializer):
    class Meta:
        model = Category
        fields = ('id', 'name',)
        read_only_fields = ('id',)

class UserSerializer(ModelSerializer):
    contacts = ClientCardSerializer(read_only=True, many=True)

    class Meta:
        model = User
        fields = ('id', 'first_name', 'email', 'last_name', 'company', 'position', 'contacts')
        read_only_fields = ('id',)

class ShopSerializer(ModelSerializer):
    class Meta:
        model = Shop
        fields = ('id', 'name', 'state', 'url', 'user')
        read_only_fields = ('id', 'user',)


class ProductSerializer(ModelSerializer):
    category = StringRelatedField()

    class Meta:
        model = Product
        fields = ( 'id', 'verbose_name', 'category')
        read_only_fields = ('id',)
class ProductInfoSerializer(ModelSerializer):
    offers = serializers.SerializerMethodField()
    product_parameters = ProductParameterSerializer(read_only=True, many=True)

    class Meta:
        model = ProductInfo
        fields = (`model`, `external_id`, `shop`, `product`, `quantity`, `price`, `price_rrc` )
        read_only_fields = ('id',)

    def get_offers(self, obj):
        offers_queryset = obj.products.filter(shop__is_active=True, shop__accepts_orders=True, quantity__gt=0)
        return ProductSerializer(offers_queryset, many=True, context=self.context).data
class ProductParameterSerializer(ModelSerializer):
    parameter = StringRelatedField()

    class Meta:
        model = ProductParameter
        fields = ('parameter', 'value',)

class OrderItemSerializer(ModelSerializer):
    product = ProductInfoSerializer(read_only=True)
    class Meta:
        model = OrderItem
        fields = ('id','quantity', 'product', 'price_at_order',)
        read_only_fields = ('id', 'price_at_order',)


class OrderItemCreateSerializer(ModelSerializer):
    product = serializers.PrimaryKeyRelatedField(queryset=Product.objects.all(), required=True)

    class OrderSerializer(ModelSerializer):
        ordered_items = OrderItemSerializer(read_only=True, many=True)
        total_sum = DecimalField(max_digits=12, decimal_places=2, read_only=True)

        contact = ClientCardSerializer(read_only=True)

        class Meta:
            model = Order
            fields = ('id', 'ordered_items', 'state', 'dt', 'total_sum', 'contact',)
            read_only_fields = ('id', 'dt', 'state', 'total_sum',)

class OrderSerializer(ModelSerializer):
    ordered_items = OrderItemCreateSerializer(read_only=True, many=True)

    total_sum = DecimalField(...)
    contact = ClientCardSerializer(read_only=True)

    class Meta:
        model = Order
        fields = ('id', 'ordered_items', 'total_sum', 'contact',)
        read_only_fields = ('id', 'state', 'dt',)
class BasketItemSerializer(serializers.Serializer):
    product_id = serializers.IntegerField(write_only=True)
    quantity = serializers.IntegerField(min_value=1, write_only=True)
