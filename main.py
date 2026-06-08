from database import init_db

from vk_api.bot_longpoll import (
    VkBotLongPoll,
    VkBotEventType
)

from vk_client import (
    community_session,
    send_message
)

from config import GROUP_ID

from keyboards import (
    main_menu_keyboard
)

from messages import (
    HELP_TEXT
)


def main():

    init_db()

    print("БД инициализирована", flush=True)

    longpoll = VkBotLongPoll(
        community_session,
        GROUP_ID
    )

    print("LongPoll запущен", flush=True)

    for event in longpoll.listen():

        if event.type != VkBotEventType.MESSAGE_NEW:
            continue

        message = event.object["message"]

        user_id = message["from_id"]

        text = (
            message.get("text", "")
            .strip()
            .lower()
        )

        print(
            f"Сообщение от {user_id}: {text}",
            flush=True
        )

        if text in [
            "/start",
            "start",
            "меню"
        ]:

            send_message(
                user_id,
                "Главное меню",
                main_menu_keyboard()
            )

        elif text in [
            "/help",
            "помощь"
        ]:

            send_message(
                user_id,
                HELP_TEXT,
                main_menu_keyboard()
            )

        else:

            send_message(
                user_id,
                "Бот работает ✅",
                main_menu_keyboard()
            )


if __name__ == "__main__":

    while True:

        try:

            main()

        except Exception as e:

            print(
                f"Ошибка: {e}",
                flush=True
            )
