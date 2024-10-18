import aiosmtplib
from email.message import EmailMessage

async def send_order_email(user_id: int, username: str, order_items: list, contact_info: str):
    order_message = f"""
    <html>
        <body>
            <h2>Уважаемые коллеги,</h2>
            <p>Вы получили новый заказ от пользователя.</p>
            <h3>Детали заказа:</h3>
            <ul>
                <li><strong>User ID:</strong> {user_id}</li>
                <li><strong>Имя пользователя:</strong> {username}</li>
            </ul>
            <h3>Заказанные товары:</h3>
            <ul>
    """

    for item in order_items:
        article, quantity = item
        order_message += f"<li><strong>Артикул:</strong> {article}, <strong>Количество:</strong> {quantity}</li>"

    order_message += f"""
            </ul>
            <h3>Контактная информация:</h3>
            <p>{contact_info}</p>
            <p>С уважением,<br>Ваша команда</p>
        </body>
    </html>
    """

    email = EmailMessage()
    email["From"] = "khanapin65@gmail.com"  # developer
    email["To"] = "khanapin65@gmail.com"    # admin
    email["Subject"] = "Новый заказ"
    email.set_content(order_message, subtype='html') 

    await aiosmtplib.send(
        email,
        hostname="smtp.gmail.com",
        port=465,
        username="khanapin65@gmail.com",
        password="uehn pkcp tuxx zwyp",
        use_tls=True
    )


async def send_contact_email(user_id: int, username: str, question: str):
    question_message = f"""
    <html>
        <body>
            <h2>Уважаемые коллеги,</h2>
            <p>Вы получили новый вопрос от пользователя.</p>
            <h3>Детали запроса:</h3>
            <ul>
                <li><strong>User ID:</strong> {user_id}</li>
                <li><strong>Имя пользователя:</strong> {username}</li>
            </ul>
            <h3>Вопрос:</h3>
            <p>{question}</p>
            <p>С уважением,<br>Ваша команда</p>
        </body>
    </html>
    """

    email = EmailMessage()
    email["From"] = "khanapin65@gmail.com"
    email["To"] = "khanapin65@gmail.com"
    email["Subject"] = "Новый вопрос"
    email.set_content(question_message, subtype='html')

    await aiosmtplib.send(
        email,
        hostname="smtp.gmail.com",
        port=465,
        username="khanapin65@gmail.com",
        password="uehn pkcp tuxx zwyp",
        use_tls=True
    )
