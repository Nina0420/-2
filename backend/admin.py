from django.contrib import admin
from django.contrib.auth.admin import UserAdmin as BaseUserAdmin
from django.utils.html import format_html
from django.urls import reverse
from backend.forms import UserCreationForm
from backend.models import (
    Category,
    User,
    Shop,
    Product,
    Contact,
    ProductInfo,
    Parameter,
    ProductParameter,
    Order,
    OrderItem,
    ClientCard,
)
from .inlines import ProductAttributeValueInline, OrderItemInline
from backend.models import Order, ProductInfo, OrderItem


class ProductAttributeValueInline(admin.TabularInline):
    model = ProductParameter
    fields = ("parameter", "value")
    raw_id_fields = ("parameter",)
    extra = 1


class OrderItemInline(admin.TabularInline):
    model = OrderItem
    fields = ("product_info", "quantity", "price")
    raw_id_fields = ("product_info", "order")
    extra = 1


@admin.register(User)
class UserAdmin(BaseUserAdmin):
    model = User
    add_form = UserCreationForm
    form = UserCreationForm
    list_display = [
        "email",
        "last_name",
        "first_name",
        "is_staff",
        "user_type",
        "company",
    ]
    search_fields = (
        "email",
        "first_name",
        "last_name",
        "company",
    )
    ordering = ("email",)
    fieldsets = (
        (None, {"fields": ("email", "password")}),
        (
            "Personal info",
            {"fields": ("first_name", "last_name", "user_type", "company")},
        ),
        (
            "Permissions",
            {
                "fields": (
                    "is_active",
                    "is_superuser",
                    "is_staff",
                    "groups",
                    "user_permissions",
                )
            },
        ),
        ("Important dates", {"fields": ("last_login", "date_joined")}),
    )
    add_fieldsets = (
        (
            None,
            {
                "classes": ("wide",),
                "fields": (
                    "email",
                    "first_name",
                    "last_name",
                    "user_type",
                    "company",
                    "password",
                    "password2",
                ),  # password2 для подтверждения пароля
            },
        ),
    )
    readonly_fields = ("last_login", "date_joined")


@admin.register(Shop)
class ShopAdmin(admin.ModelAdmin):
    list_display = ("name", "user", "is_active", "accepts_orders", "created_at")
    list_filter = ("is_active", "accepts_orders")
    search_fields = ("name", "user__email")
    raw_id_fields = ("user",)


@admin.register(Category)
class CategoryAdmin(admin.ModelAdmin):
    list_display = ("name", "parent_category")
    list_filter = ("parent_category",)
    search_fields = ("name",)


@admin.register(Product)
class ProductAdmin(admin.ModelAdmin):
    list_display = ("product_info", "shop", "quantity", "price", "uploaded_at")
    list_filter = ("shop", "product_info__category")
    search_fields = ("product_info__name", "shop__name", "external_id")
    raw_id_fields = ("product_info", "shop")


@admin.register(ProductInfo)
class ProductInfoAdmin(admin.ModelAdmin):
    list_display = ("name", "category")
    list_filter = ("category",)
    search_fields = ("name", "description")
    inlines = [ProductAttributeValueInline]


@admin.register(Parameter)
class ParameterAdmin(admin.ModelAdmin):
    pass


@admin.register(ProductParameter)
class ProductParameterAdmin(admin.ModelAdmin):
    list_display = ("product_info", "parameter", "value")
    raw_id_fields = ("product_info", "parameter")


@admin.register(Order)
class OrderAdmin(admin.ModelAdmin):
    list_display = (
        "id",
        "buyer",
        "shop",
        "status",
        "total_amount",
        "created_at",
        "updated_at",
        "contact_link",
    )
    list_filter = ("status", "shop", "created_at", "buyer")
    search_fields = ("buyer__email", "shop__name", "id")
    inlines = [OrderItemInline]
    readonly_fields = ("total_amount", "created_at", "updated_at")
    fieldsets = (
        (None, {"fields": ("buyer", "shop", "contact", "status", "total_amount")}),
        ("Даты", {"fields": ("created_at", "updated_at")}),
    )

    def contact_link(self, obj):
        if obj.contact:
            link = reverse("admin:backend_contact_change", args=[obj.contact.pk])
            contact_str = str(obj.contact)
            return format_html('&lt;a href="{}"&gt;{}&lt;/a&gt;', link, contact_str)
        return "_"

    contact_link.short_description = "Адрес доставки"


@admin.register(Contact)
class ContactAdmin(admin.ModelAdmin):
    list_display = ("user", "city", "street", "phone", "is_main")
    list_filter = ("is_main",)
    search_fields = ("user__email", "city", "street", "phone")
    raw_id_fields = ("user",)


@admin.register(OrderItem)
class OrderItemAdmin(admin.ModelAdmin):
    list_display = ("order", "product", "quantity", "price_at_order")
    list_filter = ("order__shop", "product__product_info__category")
    search_fields = ("order__id", "product__product_info__name")


@admin.register(ClientCard)
class ClientCardAdmin(admin.ModelAdmin):
    list_display = ("user", "created_at", "key")
    search_fields = ("user__email", "key")
    readonly_fields = ("key", "created_at")
    raw_id_fields = ("user",)
