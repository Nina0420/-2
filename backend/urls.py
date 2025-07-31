from backend.views import (UserActivateView, BasketView, BuyerOrderView,
                           CategoryView, ContactView, ProductViewSet
                           OrderConfirmView, OrderShopView,
)                           UserRegisterView, ShopView, UserView,
from django.urls import path, include
from rest_framework.authtoken import views as auth_views
from rest_framework.routers import DefaultRouter


router = DefaultRouter()
router.register('products', ProductViewSet, basename='products')

urlpatterns = [
    path('user/', UserView.as_view(), name='user'),
    path('register/', UserRegisterView.as_view(), name='register'),
    path('activation/<int:id>/<str:token>;/', UserActivateView.as_view(), name='activation'),
    path('order_new/', OrderConfirmView.as_view(), name='order_new'),
    path('get-token/', auth_views.obtain_auth_token),
    path('basket/', BasketView.as_view(), name='basket'),
    path('shops/', ShopView.as_view(), name='shop-list'),
    path('orders shop/', OrderShopView.as_view(), name='order-shop-list'),
    path('contacts/', ContactView.as_view(), name='contact-list'),
    path('categories/', CategoryView.as_view(), name='category-list'),

]
urlpatterns + router.urls
