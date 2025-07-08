from django.conf import settings
from django.core.mail import EmailMultiAlternatives
from django.dispatch import receiver, Signal
from django_rest_passwordreset.signals import reset_password_token_created

from backend.models import ConfirmEmailToken, User

new_user_registered = Signal(
    providing_args=['user_id'],
)

new_order = Signal(
    providing_args=['user_id'],
)


@receiver(reset_password_token_created)
def password_reset_token_created(sender, instance=None, reset_password_token, **kwargs):
    msg = EmailMultiAlternatives(
        f"Password Reset Token for {reset_password_token.user}",
        reset_password_token.key,
        settings.EMAIL_HOST_USER,
        [reset_password_token.user.email]
    )
    msg.send()

@receiver(new_user_registered)
def new_user_registered_signal(user_id, **kwargs):
    token, _ = ConfirmEmailToken.objects.get_or_create(user_id=user_id)

    msg = EmailMultiAlternatives(
        f"Password Reset Token for {token.user.email}",
        token.key,
        settings.EMAIL_HOST_USER,
        [token.user.email]
    )
    msg.send()

@receiver(new_order)
def new_order_signal(user_id, **kwargs):
    user = User.objects.get(id=user_id)

    msg = EmailMultiAlternatives(
        f"Обновление статуса заказа",
        'Заказ сформирован',
        settings.EMAIL_HOST_USER,
        [user.email]
    )
    msg.send()
