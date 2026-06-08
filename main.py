

    print(
        f"Опубликован пост {published_id} от {user_id} (анон: {anonymous})", flush=True
    )


# ==========================
# ОБРАБОТКА СООБЩЕНИЙ
# ==========================


def handle_message(user_id, text, payload_str):
    payload = {}

    if payload_str:
        try:
            payload = json.loads(payload_str)
        except Exception:
            pass

    cmd = payload.get("cmd", "")
    text_lower = text.strip().lower()

    if cmd == "my_posts" or text_lower in ["/posts", "📝 мои посты", "мои посты"]:
        show_my_posts(user_id)
        return

    if cmd == "delete_post":
        post_id = payload.get("post_id")
        if post_id:
            ask_confirm_delete(user_id, post_id)
        return

    if cmd == "confirm_delete":
        post_id = payload.get("post_id")
        if post_id:
            do_delete_post(user_id, post_id)
        return

    if cmd == "menu" or text_lower in [
        "/start",
        "start",
        "меню",
        "🏠 главное меню",
        "главное меню",
    ]:
        send_message(
            user_id,
            (
                "🏠 Главное меню\n\n"
                "Предложите пост сообществу — "
                "он будет опубликован автоматически.\n\n"
                "Добавьте «анонимно» или «#анонимно» "
                "в текст, чтобы скрыть подпись."
            ),
            main_menu_keyboard(),
        )
        return

    if cmd == "stats" or text_lower in ["/stats", "📊 статистика", "статистика"]:
        show_stats(user_id)
        return

    if cmd == "help" or text_lower in ["/help", "помощь", "❓ помощь", "help"]:
        send_message(user_id, HELP_TEXT, main_menu_keyboard())
        return

    send_message(
        user_id,
        (
            "🤖 Бот работает.\n\n"
            "Отправьте предложенный пост в сообщество "
            "или используйте кнопки меню."
        ),
        main_menu_keyboard(),
    )


def show_my_posts(user_id):
    posts = get_user_posts(user_id)

    if not posts:
        send_message(user_id, NO_POSTS, main_menu_keyboard())
        return

    lines = ["📝 Ваши опубликованные посты:\n"]

    for post in posts:
        post_id, _, pub_date, is_anon, post_text = post

        short = (post_text or "Без текста")[:50].replace("\n", " ")
        date_str = pub_date[:10] if pub_date else "—"
        anon_mark = " 🕵️" if is_anon else ""

        lines.append(f"• [{date_str}]{anon_mark} {short}…")

    send_message(user_id, "\n".join(lines), posts_keyboard(posts))


def ask_confirm_delete(user_id, post_id):
    owner = get_post_owner(post_id)

    if owner != user_id:
        send_message(user_id, DELETE_DENIED, main_menu_keyboard())
        return

    send_message(
        user_id,
        f"🗑️ Вы уверены, что хотите удалить пост #{post_id}?",
        confirm_delete_keyboard(post_id),
    )


def do_delete_post(user_id, post_id):
    if not is_member(user_id):
        send_message(user_id, NOT_MEMBER, main_menu_keyboard())
        return

    owner = get_post_owner(post_id)

    if owner != user_id:
        send_message(user_id, DELETE_DENIED, main_menu_keyboard())
        return

    try:
        delete_post(post_id)
    except Exception as e:
        print(f"Ошибка удаления поста {post_id}: {e}", flush=True)
        send_message(
            user_id,
            "❌ Не удалось удалить пост. Возможно, он уже был удалён.",
            main_menu_keyboard(),
        )
        return

    execute(
        """
        INSERT INTO logs(
            user_id, action, post_id, action_date
        ) VALUES (?, ?, ?, ?)
        """,
        (user_id, "delete", post_id, datetime.now().isoformat()),
    )

    remove_post_record(post_id)

    send_message(user_id, DELETE_SUCCESS, main_menu_keyboard())

    print(f"Пост {post_id} удалён пользователем {user_id}", flush=True)


def show_stats(user_id):
    posts = get_user_posts(user_id)
    total = len(posts)

    row = fetchone(
        """
        SELECT daily_posts, warning_count, is_blocked, block_until
        FROM user_limits
        WHERE user_id = ?
        """,
        (user_id,),
    )

    daily = row[0] if row else 0
    warnings = row[1] if row else 0
    blocked = row[2] if row else 0
    block_until = row[3] if row else None

    block_text = "Нет"

    if blocked and block_until:
        try:
            until = datetime.fromisoformat(block_until)
            block_text = f"до {until.strftime('%d.%m.%Y %H:%M')}"
        except Exception:
            block_text = "Да"

    text = (
        f"📊 Ваша статистика\n\n"
        f"📝 Постов всего: {total}\n"
        f"📅 Постов сегодня: {daily}\n"
        f"⚠️ Предупреждений: {warnings}\n"
        f"🚫 Блокировка: {block_text}"
    )

    send_message(user_id, text, main_menu_keyboard())


# ==========================
# LONGPOLL — СООБЩЕНИЯ
# ==========================


def run_bot():
    init_db()
    print("БД инициализирована", flush=True)

    poller = threading.Thread(target=process_suggestions, daemon=True)
    poller.start()

    print(
        f"Поллер предложок запущен (интервал: {SUGGESTION_POLL_INTERVAL}с)", flush=True
    )

    longpoll = VkBotLongPoll(community_session, GROUP_ID)

    print("LongPoll запущен", flush=True)

    for event in longpoll.listen():
        try:
            if event.type != VkBotEventType.MESSAGE_NEW:
                continue

            message = event.object["message"]
            user_id = message["from_id"]

            if user_id < 0:
                continue

            text = message.get("text", "")
            payload = message.get("payload", "")

            print(f"Сообщение от {user_id}: {text!r} payload={payload!r}", flush=True)

            handle_message(user_id, text, payload)

        except Exception as e:
            print(f"Ошибка обработки сообщения: {e}", flush=True)


if __name__ == "__main__":
    while True:
        try:
            run_bot()
        except Exception as e:
            print(f"Критическая ошибка: {e}", flush=True)
            time.sleep(10)
