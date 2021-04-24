# coding: utf-8
from telegram import Bot
import config


def send_telegram_message(
    message: str, chat_id=config.TELEGRAM_CHAT_ID, token=config.TELEGRAM_SENDER_TOKEN
) -> None:

    bot = Bot(token=token)
    bot.send_message(chat_id=chat_id, text=message)


if __name__ == "__main__":
    send_telegram_message("来消息了")
