from datetime import datetime, timedelta

from config import (
    DAILY_POST_LIMIT,
    WARNING_LIMIT,
    BLOCK_HOURS,
    MIN_TEXT_LENGTH,
    MAX_TEXT_LENGTH,
    POST_COOLDOWN_MINUTES,
    BLACKLIST_KEYWORDS
)

from database import (
    fetchone,
    fetchall,
    execute
)

from utils import get_post_hash


def get_user_limit(user_id):

    row = fetchone(
        """
        SELECT
            user_id,
            daily_posts,
            last_post_date,
            warning_count,
            is_blocked,
            block_until
        FROM user_limits
        WHERE user_id = ?
        """,
        (user_id,)
    )

    if row:
        return row

    execute(
        """
        INSERT INTO user_limits (
            user_id,
            daily_posts,
            warning_count,
            is_blocked
        )
        VALUES (?,0,0,0)
        """,
        (user_id,)
    )

    return fetchone(
        """
        SELECT
            user_id,
            daily_posts,
            last_post_date,
            warning_count,
            is_blocked,
            block_until
        FROM user_limits
        WHERE user_id = ?
        """,
        (user_id,)
    )


def add_warning(user_id, reason):

    data = get_user_limit(user_id)

    warnings = data[3] + 1

    if warnings >= WARNING_LIMIT:

        block_until = (
            datetime.now() +
            timedelta(hours=BLOCK_HOURS)
        )

        execute(
            """
            UPDATE user_limits
            SET
                warning_count=?,
                is_blocked=1,
                block_until=?
            WHERE user_id=?
            """,
            (
                warnings,
                block_until.isoformat(),
                user_id
            )
        )

        execute(
            """
            INSERT OR REPLACE INTO blacklist(
                user_id,
                reason,
                blocked_date
            )
            VALUES(?,?,?)
            """,
            (
                user_id,
                reason,
                datetime.now().isoformat()
            )
        )

        return (
            False,
            f"Пользователь заблокирован на "
            f"{BLOCK_HOURS} часов"
        )

    execute(
        """
        UPDATE user_limits
        SET warning_count=?
        WHERE user_id=?
        """,
        (
            warnings,
            user_id
        )
    )

    return (
        False,
        f"Предупреждение "
        f"{warnings}/{WARNING_LIMIT}: "
        f"{reason}"
    )


def check_block(user_id):

    data = get_user_limit(user_id)

    is_blocked = data[4]
    block_until = data[5]

    if not is_blocked:
        return True, ""

    if not block_until:
        return False, "Пользователь заблокирован"

    until = datetime.fromisoformat(
        block_until
    )

    if datetime.now() >= until:

        execute(
            """
            UPDATE user_limits
            SET
                is_blocked=0,
                block_until=NULL
            WHERE user_id=?
            """,
            (user_id,)
        )

        return True, ""

    return (
        False,
        f"Блокировка до "
        f"{until.strftime('%d.%m.%Y %H:%M')}"
    )


def check_text_length(text):

    if len(text) < MIN_TEXT_LENGTH:

        return (
            False,
            f"Минимальная длина "
            f"{MIN_TEXT_LENGTH}"
        )

    if len(text) > MAX_TEXT_LENGTH:

        return (
            False,
            f"Максимальная длина "
            f"{MAX_TEXT_LENGTH}"
        )

    return True, ""


def check_blacklist(text):

    lower = text.lower()

    for word in BLACKLIST_KEYWORDS:

        if word.lower() in lower:

            return (
                False,
                f"Запрещенное слово: {word}"
            )

    return True, ""


def check_daily_limit(user_id):

    row = fetchone(
        """
        SELECT
            daily_posts,
            last_post_date
        FROM user_limits
        WHERE user_id=?
        """,
        (user_id,)
    )

    if not row:
        return True, ""

    daily_posts = row[0]
    last_post_date = row[1]

    today = datetime.now().date()

    if not last_post_date:
        return True, ""

    try:

        post_date = datetime.fromisoformat(
            last_post_date
        ).date()

    except Exception:
        return True, ""

    if post_date != today:
        return True, ""

    if daily_posts >= DAILY_POST_LIMIT:

        return (
            False,
            f"Лимит "
            f"{DAILY_POST_LIMIT} постов "
            f"в день"
        )

    return True, ""


def check_duplicate(user_id, text):

    post_hash = get_post_hash(text)

    limit_date = (
        datetime.now() -
        timedelta(hours=24)
    ).isoformat()

    row = fetchone(
        """
        SELECT id
        FROM post_history
        WHERE
            user_id=?
            AND post_hash=?
            AND post_date>=?
        """,
        (
            user_id,
            post_hash,
            limit_date
        )
    )

    if row:

        return (
            False,
            "Дубликат поста "
            "за последние 24 часа"
        )

    return True, ""


def check_cooldown(user_id):

    row = fetchone(
        """
        SELECT publish_date
        FROM posts
        WHERE user_id=?
        ORDER BY publish_date DESC
        LIMIT 1
        """,
        (user_id,)
    )

    if not row:
        return True, ""

    last_publish = datetime.fromisoformat(
        row[0]
    )

    delta = (
        datetime.now() -
        last_publish
    )

    if delta.total_seconds() < (
        POST_COOLDOWN_MINUTES * 60
    ):

        return (
            False,
            f"Подождите "
            f"{POST_COOLDOWN_MINUTES} минут "
            f"между публикациями"
        )

    return True, ""


def run_antispam(user_id, text):

    checks = [
        check_block(user_id),
        check_text_length(text),
        check_blacklist(text),
        check_daily_limit(user_id),
        check_duplicate(user_id, text),
        check_cooldown(user_id)
    ]

    for result, message in checks:

        if not result:

            add_warning(
                user_id,
                message
            )

            return False, message

    return True, ""


def register_post(user_id, text):

    post_hash = get_post_hash(text)

    now = datetime.now()

    row = fetchone(
        """
        SELECT
            daily_posts,
            last_post_date
        FROM user_limits
        WHERE user_id=?
        """,
        (user_id,)
    )

    daily_posts = 0

    if row:

        daily_posts = row[0]

        try:

            last_date = (
                datetime.fromisoformat(
                    row[1]
                ).date()
                if row[1]
                else None
            )

            if last_date != now.date():
                daily_posts = 0

        except Exception:
            daily_posts = 0

    execute(
        """
        INSERT OR REPLACE INTO user_limits(
            user_id,
            daily_posts,
            last_post_date,
            warning_count,
            is_blocked,
            block_until
        )
        VALUES(
            ?,
            ?,
            ?,
            COALESCE(
                (
                    SELECT warning_count
                    FROM user_limits
                    WHERE user_id=?
                ),
                0
            ),
            COALESCE(
                (
                    SELECT is_blocked
                    FROM user_limits
                    WHERE user_id=?
                ),
                0
            ),
            (
                SELECT block_until
                FROM user_limits
                WHERE user_id=?
            )
        )
        """,
        (
            user_id,
            daily_posts + 1,
            now.isoformat(),
            user_id,
            user_id,
            user_id
        )
    )

    execute(
        """
        INSERT INTO post_history(
            user_id,
            post_hash,
            post_date
        )
        VALUES(?,?,?)
        """,
        (
            user_id,
            post_hash,
            now.isoformat()
        )
    )
