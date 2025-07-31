from django.conf import settings
from django.core.mail import EmailMultiAlternatives
from django.dispatch import receiver, Signal
from django.template.loader import render_to_string

from django_rest_passwordreset.signals import reset_password_token_created
from backend.models import User
from .tasks import send_auto_message
from backend.models import Order
FRONTEND_URL = getattr(settings, 'FRONTEND_URL', 'http://localhost:3000')
@receiver(reset_password_token_created)
def password_reset_token_created(sender, instance, reset_password_token, **kwargs):

        reset_password_url = f"{FRONTEND_URL}/password-reset/confirm/?token={reset_password_token.key}"
        try:
            html_content = render_to_string(
            'email/password_reset.html',
            {
                'user': reset_password_token.user,
                'reset_link': reset_password_url,
                'token': reset_password_token.key
            }
        )
        mail_subject = f"Сброс пароля"
        message_text = (
            f"Здравствуйте, {reset_password_token.user.first_name}!\n"
            f"Для сброса пароля перейдите по следующей ссылке: {reset_password_url}\n"
            f"Если вы не запрашивали сброс пароля, просто проигнорируйте это письмо.\n"
            f"Ваш токен для сброса: {reset_password_token.key}"
        )
        send_auto_message.delay(mail_subject, message_text, reset_password_token.user.email, html_content=html_content)

        @receiver(new_order)
        def new_order_signal(sender, user_id, order_id=None, **kwargs):

            try:
                user = User.objects.get(id=user_id)

                order = None
                if order_id:
                    try:
                        order = Order.objects.get(id=order_id)
                    except Order.DoesNotExist:
                        print(f"Error: Order with ID {order_id} not found for user {user.email}.")

                order_detail_url = f"{FRONTEND_URL}/my-orders/{order_id}/" if order_id else FRONTEND_URL

                html_content = render_to_string(
                'email/new_order.html',
                {
                    'user': user,
                    'order': order,
                    'order_detail_url': order_detail_url,
                    'status_message': 'Ваш заказ успешно сформирован и принят в обработку.'
                }
            )
            if order:
                mail_subject = f"Ваш заказ №{order.id} успешно сформирован"
                message_text = (
                    f"Здравствуйте, {user.first_name}!\n"
                    f"Ваш заказ №{order.id} успешно сформирован и принят в обработку.\n"
                    f"Вы можете отслеживать его по ссылке: {order_detail_url}\n"
                    f"Спасибо за покупку!"
                )
            else:
            mail_subject = "Информация о вашем заказе"
            message_text = (
                f"Здравствуйте, {user.first_name}!\n"
                f"Ваш заказ был принят в обработку.\n"
                f"Вы можете отслеживать его по ссылке: {order_detail_url}\n"
                f"Спасибо за покупку!"
            )

            send_auto_message.delay(mail_subject, message_text, user.email, html_content=html_content)
            print(f"Order notification email sent to {user.email} for order ID {order_id}")
