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
    HELP_TEXT,
    NO_POSTS
)


def handle_message(user_id, text):

    text = text.strip().lower()

    if text in [
        "/start",
        "start",
        "меню"
    ]:

        send_message(
            user_id,
            "🏠 Главное меню",
            main_menu_keyboard()
        )

        return

    if text in [
        "/help",
        "помощь",
        "❓ помощь"
    ]:

        send_message(
            user_id,
            HELP_TEXT,
            main_menu_keyboard()
        )

        return

    if text in [
        "/stats",
        "📊 статистика"
    ]:

        send_message(
            user_id,
            (
                "📊 Статистика\n\n"
                "Функция находится в разработке"
            ),
            main_menu_keyboard()
        )

        return

    if text in [
        "/posts",
        "📝 мои посты"
    ]:

        send_message(
            user_id,
            NO_POSTS,
            main_menu_keyboard()
        )

        return

    send_message(
        user_id,
        (
            "🤖 Бот работает.\n\n"
            "Используйте кнопки меню."
        ),
        main_menu_keyboard()
    )


def run_bot():

    init_db()

    print(
        "БД инициализирована",
        flush=True
    )

    longpoll = VkBotLongPoll(
        community_session,
        GROUP_ID
    )

    print(
        "LongPoll запущен",
        flush=True
    )

    for event in longpoll.listen():

        try:

            if event.type != VkBotEventType.MESSAGE_NEW:
                continue

            message = event.object["message"]

            user_id = message["from_id"]

            text = message.get(
                "text",
                ""
            )

            print(
                f"Сообщение от {user_id}: {text}",
                flush=True
            )

            handle_message(
                user_id,
                text
            )

        except Exception as e:

            print(
                f"Ошибка обработки сообщения: {e}",
                flush=True
            )


if __name__ == "__main__":

    while True:

        try:

            run_bot()

        except Exception as e:

            print(
                f"Ошибка: {e}",
                flush=True
            )
