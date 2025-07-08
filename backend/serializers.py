from backend.models import (Category, Order,  OrderItem, Product, ProductInfo, ProductParameter, Shop)

class ContactSerializer(ModelSerializer):

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
    contacts = ContactSerializer(read_only=True, many=True)

    class Meta:
        model = User
        fields = ('id', 'first_name', 'email', 'last_name', 'company', 'position', 'contacts')
        read_only_fields = ('id',)

class ShopSerializer(ModelSerializer):
    class Meta:
        model = Shop
        fields = ('id', 'name', 'state',)
        read_only_fields = ('id',)


class ProductSerializer(ModelSerializer):
    category = StringRelatedField()

    class Meta:
        model = Product
        fields = ('name', 'category',)

class ProductInfoSerializer(ModelSerializer):
    product = ProductSerializer(read_only=True)
    product_parameters = ProductParameterSerializer(read_only=True, many=True)

    class Meta:
        model = ProductInfo
        fields = ('id', 'model', 'product', 'shop', 'quantity', 'price', 'price_rrc', 'product_parameters',)
        read_only_fields = ('id',)

class ProductParameterSerializer(ModelSerializer):
    parameter = StringRelatedField()

    class Meta:
        model = ProductParameter
        fields = ('parameter', 'value',)

class OrderItemSerializer(ModelSerializer):
    class Meta:
        model = OrderItem
        fields = ('id','quantity', 'product_info', 'order',)
        read_only_fields = ('id',)
        extra_kwargs = {
            'order': {'write_only': True}
        }


class OrderItemCreateSerializer(OrderItemSerializer):
    product_info = ProductInfoSerializer(read_only=True)


class OrderSerializer(ModelSerializer):
    ordered_items = OrderItemCreateSerializer(read_only=True, many=True)

    total_sum = IntegerField()
    contact = ContactSerializer(read_only=True)

    class Meta:
        model = Order
        fields = ('id', 'ordered_items', 'state', 'dt', 'total_sum', 'contact',)
        read_only_fields = ('id',)
