import vk_api

from vk_api.utils import get_random_id

from config import (
    USER_TOKEN,
    COMMUNITY_TOKEN,
    GROUP_ID,
    OWNER_ID
)


# ==========================
# СЕССИИ VK
# ==========================

user_session = vk_api.VkApi(
    token=USER_TOKEN
)

user_vk = user_session.get_api()

community_session = vk_api.VkApi(
    token=COMMUNITY_TOKEN
)

community_vk = community_session.get_api()


# ==========================
# СООБЩЕНИЯ
# ==========================

def send_message(
    user_id,
    text,
    keyboard=None
):

    community_vk.messages.send(
        user_id=user_id,
        random_id=get_random_id(),
        message=text,
        keyboard=keyboard
    )


# ==========================
# ПОДПИСКА НА ГРУППУ
# ==========================

def is_member(user_id):

    try:

        result = user_vk.groups.isMember(
            group_id=GROUP_ID,
            user_id=user_id
        )

        return bool(result)

    except Exception:

        return False


# ==========================
# ПОЛУЧЕНИЕ ПРЕДЛОЖКИ
# ==========================

def get_suggestions():

    try:

        result = user_vk.wall.getSuggestions(
            owner_id=OWNER_ID,
            count=100
        )

        return result.get(
            "items",
            []
        )

    except Exception as e:

        print(
            "Ошибка получения предложки:",
            e
        )

        return []


# ==========================
# ПУБЛИКАЦИЯ ПОСТА
# ==========================

def publish_post(
    text,
    attachments="",
    anonymous=False
):

    signed = 0 if anonymous else 1

    result = user_vk.wall.post(
        owner_id=OWNER_ID,
        from_group=1,
        message=text,
        attachments=attachments,
        signed=signed
    )

    return result["post_id"]


# ==========================
# УДАЛЕНИЕ ПОСТА
# ==========================

def delete_post(post_id):

    return user_vk.wall.delete(
        owner_id=OWNER_ID,
        post_id=post_id
    )
