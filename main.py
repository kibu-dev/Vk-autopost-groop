import json
import traceback

import vk_api

from vk_api.bot_longpoll import (
    VkBotLongPoll,
    VkBotEventType
)

from config import (
    COMMUNITY_TOKEN,
    GROUP_ID
)

from database import (
    init_db,
    execute,
    fetchall,
    fetchone
)

from keyboards import (
    main_menu_keyboard,
    posts_keyboard,
    confirm_delete_keyboard
)

from messages import (
    SUCCESS_PUBLISH,
    NO_POSTS,
    DELETE_DENIED,
    NOT_MEMBER,
    DELETE_SUCCESS,
    HELP_TEXT
)

from utils import (
    remove_anonymous_marker
)

from anti_spam import (
    run_antispam,
    register_post
)

from vk_client import (
    send_message,
    publish_post,
    delete_post,
    is_member
)

# ====================================
# ОБРАБОТКА КНОПОК
# ====================================

def show_menu(user_id):
    send_message(
        user_id,
        "🏠 Главное меню",
        main_menu_keyboard()
    )

def show_my_posts(user_id):

    posts = fetchall(
        """
        SELECT *
        FROM posts
        WHERE user_id=?
        ORDER BY publish_date DESC
        """,
        (user_id,)
    )

    if not posts:

        send_message(
            user_id,
            NO_POSTS,
            main_menu_keyboard()
        )

        return

    send_message(
        user_id,
        "📝 Ваши публикации:",
        posts_keyboard(posts)
    )

def show_stats(user_id):

    count = fetchone(
        """
        SELECT COUNT(*)
        FROM posts
        WHERE user_id=?
        """,
        (user_id,)
    )[0]

    send_message(
        user_id,
        f"📊 Опубликовано постов: {count}",
        main_menu_keyboard()
    )

# ====================================
# УДАЛЕНИЕ ПОСТОВ
# ====================================

def request_delete(user_id, post_id):

    row = fetchone(
        """
        SELECT post_id
        FROM posts
        WHERE
            post_id=?
            AND user_id=?
        """,
        (
            post_id,
            user_id
        )
    )

    if not row:

        send_message(
            user_id,
            DELETE_DENIED,
            main_menu_keyboard()
        )

        return

    send_message(
        user_id,
        "Подтвердите удаление",
        confirm_delete_keyboard(post_id)
    )

def confirm_delete(user_id, post_id):

    if not is_member(user_id):

        send_message(
            user_id,
            NOT_MEMBER,
            main_menu_keyboard()
        )

        return

    row = fetchone(
        """
        SELECT post_id
        FROM posts
        WHERE
            post_id=?
            AND user_id=?
        """,
        (
            post_id,
            user_id
        )
    )

    if not row:

        send_message(
            user_id,
            DELETE_DENIED,
            main_menu_keyboard()
        )

        return

    try:

        delete_post(post_id)

        execute(
            """
            DELETE FROM posts
            WHERE post_id=?
            """,
            (post_id,)
        )

        send_message(
            user_id,
            DELETE_SUCCESS,
            main_menu_keyboard()
        )

    except Exception as e:

        send_message(
            user_id,
            f"Ошибка удаления: {e}",
            main_menu_keyboard()
        )

# ====================================
# ПУБЛИКАЦИЯ
# ====================================

def handle_post(user_id, text):

    ok, reason = run_antispam(
        user_id,
        text
    )

    if not ok:

        send_message(
            user_id,
            f"⛔ {reason}",
            main_menu_keyboard()
        )

        return

    cleaned_text, anonymous = (
        remove_anonymous_marker(text)
    )

    try:

        post_id = publish_post(
            text=cleaned_text,
            anonymous=anonymous
        )

        execute(
            """
            INSERT INTO posts(
                post_id,
                user_id,
                publish_date,
                is_anonymous,
                post_text
        )
            VALUES(?,?,?,?,?)
            """,
            (
                post_id,
                user_id,
                __import__("datetime")
                .datetime.now()
                .isoformat(),
                int(anonymous),
                cleaned_text
            )
        )

        register_post(
            user_id,
            cleaned_text
        )

        send_message(
            user_id,
            SUCCESS_PUBLISH,
            main_menu_keyboard()
        )

    except Exception as e:

        send_message(
            user_id,
            f"Ошибка публикации:\n{e}"
        )

# ====================================
# PAYLOAD
# ====================================

def handle_payload(user_id, payload):

    cmd = payload.get("cmd")

    if cmd == "menu":
        show_menu(user_id)

    elif cmd == "help":

        send_message(
            user_id,
            HELP_TEXT,
            main_menu_keyboard()
        )

    elif cmd == "my_posts":
        show_my_posts(user_id)

    elif cmd == "stats":
        show_stats(user_id)

    elif cmd == "delete_post":

        request_delete(
            user_id,
            payload.get("post_id")
        )

    elif cmd == "confirm_delete":

        confirm_delete(
            user_id,
            payload.get("post_id")
        )

# ====================================
# LONGPOLL
# ====================================

def main():

    init_db()

    vk_session = vk_api.VkApi(
        token=COMMUNITY_TOKEN
    )

    longpoll = VkBotLongPoll(
        vk_session,
        GROUP_ID
    )

    print("Бот запущен")

    for event in longpoll.listen():

        try:

            if (
                event.type
                != VkBotEventType.MESSAGE_NEW
            ):
                continue

            message = (
                event.object["message"]
            )

            user_id = message["from_id"]

            text = (
                message.get("text", "")
                .strip()
            )

            payload = message.get(
                "payload"
            )

            if payload:

                handle_payload(
                    user_id,
                    json.loads(payload)
                )

                continue

            if text.lower() in (
                "меню",
                "start",
                "/start"
            ):

                show_menu(user_id)

                continue

            handle_post(
                user_id,
                text
            )

        except Exception:

            traceback.print_exc()

if __name__ == "__main__":
    main()
