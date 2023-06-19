import logging
import os

import requests
import telebot
from dotenv import load_dotenv
import schedule

load_dotenv(".env")
load_dotenv(".env.secret")

logging.basicConfig(format="%(name)s - %(levelname)s - %(message)s",
                    level=logging.INFO)
logger = logging.getLogger("Bot")

bot = telebot.TeleBot(os.getenv("SECRET_BOT_TOKEN"))
api_access_key = os.getenv("SECRET_API_KEY")
api_url = os.getenv("SECRET_API_URL").rstrip('/')


def get_request_api(endpoint: str, params=None) -> dict:
    url = f"{api_url}/{endpoint.lstrip('/')}"
    if params is None:
        params = {}
    params = {'secret-key': api_access_key, **params}
    result = requests.get(url, params=params)
    return result.json()


def post_request_api(endpoint: str, data=None) -> dict:
    url = f"{api_url}/{endpoint.lstrip('/')}"
    if data is None:
        data = {}
    params = {'secret-key': api_access_key}
    result = requests.post(url, params=params, json=data)
    return result.json()


def is_account_connected(user_id: int):
    response = get_request_api(f"/telegram-account/{user_id}")
    return response["success"] and response["connected"]


@bot.message_handler(commands=["start", "help", "info"])
def command_help(message):
    info_string = "Вас приветствует бот уведомлений Electro Guidebook!"
    if is_account_connected(message.chat.id):
        status_line = "Ваш аккаунт подключён к для отправки уведомлений"
    else:
        status_line = "Ваш аккаунт не подключён для отправки уведомлений. Введите ваш email и код с сайта для подключения."
    lines = [info_string, status_line]
    bot.send_message(message.chat.id, "\n\n".join(lines))


@bot.message_handler(commands=["commands"])
def command_commands(message):
    commands = ["/start", "/help", "/info", "/commands"]
    bot.send_message(message.chat.id, "\n".join(commands))


@bot.message_handler()
def handle_message(message):
    if is_account_connected(message.chat.id):
        bot.reply_to(message, "Вы уже подключили аккаунт. Ожидайте уведомлений")
        return
    lines = message.text.strip().split('\n')
    if len(lines) != 2:
        bot.reply_to(message, "Введите email и код со страницы профиля в формате:\n\n<email>\n<код>, "
                              "\n\nнапример:\nmail@example.com\n12345678")
        return
    email, verification_code = lines
    data = {
        "user-email": email,
        "verification-code": verification_code,
        "account-username": message.chat.username
    }
    response = post_request_api(f"/telegram-account/{message.chat.id}", data=data)
    if response["success"]:
        bot.reply_to(message, "Аккаунт успешно подключён! Ожидайте уведомлений")
    elif response["message"] in {"no-user-with-email", "wrong-verification-code"}:
        bot.reply_to(message, "Email или код неверны. Проверьте данные и попробуйте ещё раз.")
    elif response["message"] == "user-already-connected":
        bot.reply_to(message, "Уведомления уже настроены для другого аккаунта Telegram. Отключите их и попробуйте ещё раз.")
    else:
        bot.reply_to(message, "Что-то пошло не так... Проверьте данные и попробуйте ещё раз.")


def handle_updates():
    updates = bot.get_updates(offset=(bot.last_update_id + 1), long_polling_timeout=10)
    if len(updates) > 0:
        bot.process_new_updates(updates)
        logger.info("Received and processed %s updates", len(updates))
    else:
        logger.info("No updates received")


def handle_notifications():
    base_url = os.getenv("BASE_URL")
    notifications = get_request_api("/pending-notifications")["notifications"]
    for notification in notifications:
        notification_id = notification["notification"]["id"]
        user_id = notification["account"]["telegram-id"]
        text = notification["notification"]["text"]
        link = notification["notification"]["link"]
        if link is not None:
            link = f"{base_url.rstrip('/')}/{link.lstrip('/')}"
            link = telebot.formatting.hlink("Подробнее", link)
            text += f"\n\n{link}"
        bot.send_message(user_id, text, parse_mode="html")
        post_request_api(f"/pending-notifications/{notification_id}/delivered")
    if len(notifications) == 0:
        logger.info("No pending notifications")
    else:
        logger.info(f"Processed {len(notifications)} notifications")


def main():
    running = True
    schedule.every().second.do(handle_updates)
    schedule.every().minute.do(handle_notifications)
    logger.warning("Starting...")
    while running:
        try:
            schedule.run_pending()
        except KeyboardInterrupt:
            logger.warning("Exiting...")
            running = False


if __name__ == '__main__':
    main()
