
from rest_framework.authtoken.models import Token
from rest_framework.generics import ListAPIView
from rest_framework.response import Response
from rest_framework.views import APIView
from rest_framework import status
from .exceptions import ItemNotFound, InsufficientStock
from .models import ProductInfo
from rest_framework.exceptions import ValidationError as DRFValidationError
rom rest_framework.permissions import IsAuthenticated
from .serializers import BasketItemSerializer
from backend.models import Shop, Category, Product, ProductInfo, Parameter, ProductParameter, Order, OrderItem, \
    Contact, ConfirmEmailToken
from backend.serializers import UserSerializer, CategorySerializer, ShopSerializer, ProductInfoSerializer, \
    OrderItemSerializer, OrderSerializer, ContactSerializer
from backend.signals import new_user_registered, new_order
from backend.serializers import (UserSerializer, CategorySerializer, ShopSerializer, ProductInfoSerializer,
                                       OrderItemSerializer, OrderSerializer, ContactSerializer,
                                       RegisterAccountSerializer, ConfirmAccountSerializer, PasswordChangeSerializer)

from django.contrib.auth import authenticate
from django.contrib.auth.password_validation import validate_password
from django.core.exceptions import ValidationError as DjangoValidationError
from django.db import IntegrityError
from django.http import JsonResponse



class RegisterAccountSerializer(APIView):
    def post(self, request, *args, **kwargs):
        serializer = RegisterAccountSerializer(data=request.data)
        serializer.is_valid(raise_exception=True)
        try:
            user = User.objects.create_user(
                email=serializer.validated_data['email'],
                password=serializer.validated_data['password'],
                first_name=serializer.validated_data['first_name'],
                last_name=serializer.validated_data['last_name'],
                company=serializer.validated_data.get('company', ''),
                position=serializer.validated_data.get('position', ''),
                is_active=False             )

            new_user_registered.send(sender=self.__class__, user_id=user.id) # Используем self.__class__
            return Response({'Status': True, 'message': 'Регистрация успешна. Проверьте ваш email для активации.'}, status=status.HTTP_201_CREATED)
        except IntegrityError as e:
            return Response({'Status': False, 'Errors': {'email': 'Пользователь с таким email уже существует.'}}, status=status.HTTP_400_BAD_REQUEST)
        except Exception as e:
            return Response({'Status': False, 'Errors': f'Произошла непредвиденная ошибка: {e}'}, status=status.HTTP_500_INTERNAL_SERVER_ERROR)



class ConfirmAccount(APIView):

    def post(self, request, *args, **kwargs):
        serializer = ConfirmAccountSerializer(data=request.data)
        serializer.is_valid(raise_exception=True)

        email = serializer.validated_data['email']
        token_key = serializer.validated_data['token']

        token = ConfirmEmailToken.objects.filter(user__email=email, key=token_key).first()
        if token:
            token.user.is_active = True
            token.user.save()
            token.delete()
            return Response({'Status': True, 'message': 'Аккаунт успешно активирован.'}, status=status.HTTP_200_OK)
        else:
            return Response({'Status': False, 'Errors': 'Неправильно указан токен или email.'},
                            status=status.HTTP_400_BAD_REQUEST)


class AccountDetails(APIView):
    permission_classes = [IsAuthenticated]
    def get(self, request, *args, **kwargs):
        serializer = UserSerializer(request.user)
        return Response(serializer.data, status=status.HTTP_200_OK)

    def post(self, request, *args, **kwargs):
        if 'password' in request.data:
            serializer = PasswordChangeSerializer(data=request.data)
            serializer.is_valid(raise_exception=True)
            serializer.save()
            return Response({'Status': True, 'message': 'Пароль успешно изменен.'}, status=status.HTTP_200_OK)

            request.user.set_password(serializer.validated_data['password'])
            request.user.save()
            return Response({'Status': True, 'message': 'Пароль успешно изменен.'}, status=status.HTTP_200_OK)
        else:

            serializer = UserSerializer(request.user, data=request.data,
                                        partial=True)
            serializer.is_valid(raise_exception=True)
            serializer.save()
            return Response({'Status': True, 'message': 'Данные аккаунта успешно обновлены.'},
                            status=status.HTTP_200_OK)


class LoginAccount(APIView):
    def post(self, request, *args, **kwargs):
        serializer = LoginSerializer(data=request.data)
        serializer.is_valid(raise_exception=True)
        user = serializer.validated_data['user']
        token, created = Token.objects.get_or_create(user=user)
        return Response({'Status': True, 'token': token.key}, status=status.HTTP_200_OK)
class ShopView(ListAPIView):
    queryset = Shop.objects.filter(state=True)
    serializer_class = ShopSerializer


class CategoryView(ListAPIView):
    queryset = Category.objects.all()
    serializer_class = CategorySerializer


class ProductInfoView(APIView):
    def get(self, request, *args, **kwargs):

        query = Q(shop__state=True)
        shop_id = request.query_params.get('shop_id')
        category_id = request.query_params.get('category_id')

        if shop_id:
            query = query & Q(shop_id=shop_id)

        if category_id:
            query = query & Q(product__category_id=category_id)

        queryset = ProductInfo.objects.filter(
            query).select_related(
            'shop', 'product__category').prefetch_related(
            'product_parameters__parameter').distinct()

        serializer = ProductInfoSerializer(queryset, many=True)

        return Response(serializer.data, status=status.HTTP_200_OK)


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

            response_data = {...}  #
            return Response(response_data, status=status.HTTP_201_CREATED)

        except ProductInfo.DoesNotExist:

            raise ItemNotFound(detail="Указанный товар не найден или недоступен.")
        except InsufficientStock as e:

            return Response({"detail": str(e)}, status=status.HTTP_400_BAD_REQUEST)

class PartnerUpdate(APIView):

    def post(self, request, *args, **kwargs):
        if not request.user.is_authenticated:
            return JsonResponse({'Status': False, 'Error': 'Log in required'}, status=403)

        if request.user.type != 'shop':
            return JsonResponse({'Status': False, 'Error': 'Только для магазинов'}, status=403)

        url = request.data.get('url')
        if url:
            validate_url = URLValidator()
            try:
                validate_url(url)
            except ValidationError as e:
                return JsonResponse({'Status': False, 'Error': str(e)})
            else:
                stream = get(url).content

                data = load_yaml(stream, Loader=Loader)

                shop, _ = Shop.objects.get_or_create(name=data['shop'], user_id=request.user.id)
                for category in data['categories']:
                    category_object, _ = Category.objects.get_or_create(id=category['id'], name=category['name'])
                    category_object.shops.add(shop.id)
                    category_object.save()
                ProductInfo.objects.filter(shop_id=shop.id).delete()
                for item in data['goods']:
                    product, _ = Product.objects.get_or_create(name=item['name'], category_id=item['category'])

                    product_info = ProductInfo.objects.create(product_id=product.id,
                                                              external_id=item['id'],
                                                              model=item['model'],
                                                              price=item['price'],
                                                              price_rrc=item['price_rrc'],
                                                              quantity=item['quantity'],
                                                              shop_id=shop.id)
                    for name, value in item['parameters'].items():
                        parameter_object, _ = Parameter.objects.get_or_create(name=name)
                        ProductParameter.objects.create(product_info_id=product_info.id,
                                                        parameter_id=parameter_object.id,
                                                        value=value)

                return JsonResponse({'Status': True})

        return JsonResponse({'Status': False, 'Errors': 'Не указаны все необходимые аргументы'})
class PartnerOrders(APIView):

    def get(self, request, *args, **kwargs):
        if not request.user.is_authenticated:
            return JsonResponse({'Status': False, 'Error': 'Log in required'}, status=403)

        if request.user.type != 'shop':
            return JsonResponse({'Status': False, 'Error': 'Только для магазинов'}, status=403)

        order = Order.objects.filter(
            ordered_items__product_info__shop__user_id=request.user.id).exclude(state='basket').prefetch_related(
            'ordered_items__product_info__product__category',
            'ordered_items__product_info__product_parameters__parameter').select_related('contact').annotate(
            total_sum=Sum(F('ordered_items__quantity') * F('ordered_items__product_info__price'))).order_by('id'). distinct()

        serializer = OrderSerializer(order, many=True)
        return Response(serializer.data)
class ContactView(APIView):

    def get(self, request, *args, **kwargs):
        if not request.user.is_authenticated:
            return JsonResponse({'Status': False, 'Error': 'Log in required'}, status=403)
        contact = Contact.objects.filter(
            user_id=request.user.id)
        serializer = ContactSerializer(contact, many=True)
        return Response(serializer.data)
    def post(self, request, *args, **kwargs):
        if not request.user.is_authenticated:
            return JsonResponse({'Status': False, 'Error': 'Log in required'}, status=403)

        if {'city', 'street', 'phone'}.issubset(request.data):
            request.data._mutable = True
            request.data.update({'user': request.user.id})
            serializer = ContactSerializer(data=request.data)

            if serializer.is_valid():
                serializer.save()
                return JsonResponse({'Status': True}, status=status.HTTP_201_CREATED)
            else:
                return JsonResponse({'Status': False, 'Errors': serializer.errors} , status=status.HTTP_400_BAD_REQUEST)

        return JsonResponse({'Status': False, 'Errors': 'Не указаны все необходимые аргументы'})

    def delete(self, request, *args, **kwargs):
        if not request.user.is_authenticated:
            return JsonResponse({'Status': False, 'Error': 'Log in required'}, status=403)

        items_sting = request.data.get('items')
        if items_sting:
            items_list = items_sting.split(',')
            query = Q()
            objects_deleted = False
            for contact_id in items_list:
                if contact_id.isdigit():
                    query = query | Q(user_id=request.user.id, id=contact_id)
                    objects_deleted = True

            if objects_deleted:
                deleted_count = Contact.objects.filter(query).delete()[0]
                return JsonResponse({'Status': True, 'Удалено объектов': deleted_count})
        return JsonResponse({'Status': False, 'Errors': 'Не указаны все необходимые аргументы'})

    def put(self, request, *args, **kwargs):
        if not request.user.is_authenticated:
            return JsonResponse({'Status': False, 'Error': 'Log in required'}, status=403)

        if 'id' in request.data:
            if request.data['id'].isdigit():
                contact = Contact.objects.filter(id=request.data['id'], user_id=request.user.id).first()
                print(contact)
                if contact:
                    serializer = ContactSerializer(contact, data=request.data, partial=True)
                    if serializer.is_valid():
                        serializer.save()
                        return JsonResponse({'Status': True})
                    else:
                        JsonResponse({'Status': False, 'Errors': serializer.errors})

        return JsonResponse({'Status': False, 'Errors': 'Не указаны все необходимые аргументы'})


class OrderView(APIView):

    def get(self, request, *args, **kwargs):
        if not request.user.is_authenticated:
            return JsonResponse({'Status': False, 'Error': 'Log in required'}, status=403)
        order = Order.objects.filter(
            user_id=request.user.id).exclude(state='basket').prefetch_related(
            'ordered_items__product_info__product__category',
            'ordered_items__product_info__product_parameters__parameter').select_related('contact').annotate(
            total_sum=Sum(F('ordered_items__quantity') * F('ordered_items__product_info__price'))).distinct()

        serializer = OrderSerializer(order, many=True)
        return Response(serializer.data)
    def post(self, request, *args, **kwargs):
        if not request.user.is_authenticated:
            return JsonResponse({'Status': False, 'Error': 'Log in required'}, status=403)

        if {'id', 'contact'}.issubset(request.data):
            if request.data['id'].isdigit():
                try:
                    is_updated = Order.objects.filter(
                        user_id=request.user.id, id=request.data['id']).update(
                        contact_id=request.data['contact'],
                        state='new')
                except IntegrityError as error:
                    print(error)
                    return JsonResponse({'Status': False, 'Errors': 'Неправильно указаны аргументы'})
                else:
                    if is_updated:
                        new_order.send(sender=self.__class__, user_id=request.user.id)
                        return JsonResponse({'Status': True})

        return JsonResponse({'Status': False, 'Errors': 'Не указаны все необходимые аргументы'})


class UserActivateView:
    pass