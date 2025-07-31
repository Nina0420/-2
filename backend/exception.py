from rest_framework.exceptions import APIException
from rest_framework.response import APIView
from rest_framework.response import Response
from rest_framework import status
from .exceptions import ItemNotFound, InsufficientStock
from .models import ProductInfo
from .serializers import BasketItemSerializer
class BasketView(APIView):
        def post(self, request, *args, **kwargs):
            serializer = BasketItemSerializer(data=request.data)
            serializer.is_valid(raise_exception=True)

            product_id = serializer.validated_data['product_id']
            quantity = serializer.validated_data['quantity']

            try:

            product_info = ProductInfo.objects.get(
                id=product_id,
                shop__state=True,
                shop__is_active=True,
                shop__accepts_orders=True
            )
            if product_info.quantity & lt; quantity:
                raise InsufficientStock(
                    detail=f'Недостаточно "{product_info.model}" в наличии от "{product_info.shop.name}". Доступно: {product_info.quantity}.'
                )
class InvalidActivationCode(APIException):
    status_code = 404
    default_detail = 'Activation link is invalid'
    default_code = 'Incorrect data'

class ItemNotFound(APIException):

    status_code = 404
    default_detail = 'The requested item was not found.'
    default_code = 'item_not_found'

class InsufficientStock(APIException):

    status_code = 400
    default_detail = 'Insufficient stock available.'
    default_code = 'insufficient_stock'
