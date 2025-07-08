from django.contrib import admin
from django.contrib.auth.admin import UserAdmin
from backend.models import Category, User, Shop, Product, Contact,ProductInfo, Parameter, ProductParameter, Order, OrderItem, \
    ConfirmEmailToken

@admin.register(User)
class UserAdmin(UserAdmin):
    model = User

    fieldsets = (
        (None, {'fields': ('email','type', 'password')}),
        ('Personal info', {'fields': ('first_name', 'last_name', 'position', 'company')}),
        ('Permissions'),
         {
            'fields': (
                'is_active',
                'is_superuser',
                'is_staff',
                'is superuser'
                'groups',
                'user_permissions',
            ),
        },
        (('Important dates'), {'fields': ('last_login', 'date_joined')}),
    )
    list_display = ('email', 'last_name', 'first_name', 'is_staff')
@admin.register(Shop)
class ShopAdmin(admin.ModelAdmin):
    pass
@admin.register(Category)
class CategoryAdmin(admin.ModelAdmin):
    pass
@admin.register(Product)
class ProductAdmin(admin.ModelAdmin):
    pass
@admin.register(ProductInfo)
class ProductInfoAdmin(admin.ModelAdmin):
    pass
@admin.register(Parameter)
class ParameterAdmin(admin.ModelAdmin):
    pass
@admin.register(ProductParameter)
class ProductParameterAdmin(admin.ModelAdmin):
    pass
@admin.register(Order)
class OrderAdmin(admin.ModelAdmin):
    pass
@admin.register(Contact)
class ContactAdmin(admin.ModelAdmin):
    pass
@admin.register(OrderItem)
class OrderItemAdmin(admin.ModelAdmin):
    pass
@admin.register(ConfirmEmailToken)
class ConfirmEmailTokenAdmin(admin.ModelAdmin):
    list_display = ('user', 'created_at', 'key')
