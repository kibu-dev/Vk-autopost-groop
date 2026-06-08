import json
from vk_api.keyboard import VkKeyboard, VkKeyboardColor


def main_menu_keyboard():
    keyboard = VkKeyboard(one_time=False)

    keyboard.add_button(
        "📝 Мои посты",
        color=VkKeyboardColor.PRIMARY,
        payload=json.dumps({
            "cmd": "my_posts"
        })
    )

    keyboard.add_button(
        "📊 Статистика",
        color=VkKeyboardColor.SECONDARY,
        payload=json.dumps({
            "cmd": "stats"
        })
    )

    keyboard.add_line()

    keyboard.add_button(
        "❓ Помощь",
        color=VkKeyboardColor.SECONDARY,
        payload=json.dumps({
            "cmd": "help"
        })
    )

    return keyboard.get_keyboard()


def posts_keyboard(posts):
    keyboard = VkKeyboard(one_time=False)

    for post in posts[:10]:

        post_id = post[0]
        text = post[4] or "Без текста"

        short_text = text.replace("\n", " ")[:30]

        keyboard.add_button(
            f"🗑️ {short_text}",
            color=VkKeyboardColor.NEGATIVE,
            payload=json.dumps({
                "cmd": "delete_post",
                "post_id": post_id
            })
        )

        keyboard.add_line()

    keyboard.add_button(
        "🏠 Главное меню",
        color=VkKeyboardColor.SECONDARY,
        payload=json.dumps({
            "cmd": "menu"
        })
    )

    return keyboard.get_keyboard()


def confirm_delete_keyboard(post_id):
    keyboard = VkKeyboard(one_time=False)

    keyboard.add_button(
        "✅ Да, удалить",
        color=VkKeyboardColor.NEGATIVE,
        payload=json.dumps({
            "cmd": "confirm_delete",
            "post_id": post_id
        })
    )

    keyboard.add_button(
        "❌ Отмена",
        color=VkKeyboardColor.SECONDARY,
        payload=json.dumps({
            "cmd": "menu"
        })
    )

    return keyboard.get_keyboard()
