import aiosmtplib
from email.message import EmailMessage

async def send_order_email(user_id: int, username: str, order_items: list, contact_info: str):

    order_message = f"Новый заказ от пользователя:\n\n" \
                    f"User ID: {user_id}\n" \
                    f"Имя пользователя: {username}\n\n" \
                    f"Заказанные товары:\n"

    for item in order_items:
        article, quantity = item
        order_message += f"Артикул: {article}, Количество: {quantity}\n"

    order_message += f"\nКонтактная информация:\n{contact_info}\n"

    email = EmailMessage()
    email["From"] = "khanapin65@gmail.com" # developer
    email["To"] = "khanapin65@gmail.com" # admin
    email["Subject"] = "Новый заказ"
    email.set_content(order_message)

    await aiosmtplib.send(
        email,
        hostname="smtp.gmail.com",
        port=465,
        username="khanapin65@gmail.com",
        password="uehn pkcp tuxx zwyp",
        use_tls=True
    )


async def send_contact_email(user_id: int, username: str, question: str):
    question_message = f"Новый вопрос от пользователя:\n\n" \
                       f"User ID: {user_id}\n" \
                       f"Имя пользователя: {username}\n\n" \
                       f"Вопрос:\n{question}\n" \

    email = EmailMessage()
    email["From"] = "khanapin65@gmail.com"
    email["To"] = "khanapin65@gmail.com"
    email["Subject"] = "Новый вопрос"
    email.set_content(question_message)

    await aiosmtplib.send(
        email,
        hostname="smtp.gmail.com",
        port=465,
        username="khanapin65@gmail.com",
        password="uehn pkcp tuxx zwyp",
        use_tls=True
    )


