import os
from dotenv import load_dotenv

load_dotenv()

# ==========================
# VK
# ==========================

USER_TOKEN = os.getenv("USER_TOKEN")
COMMUNITY_TOKEN = os.getenv("COMMUNITY_TOKEN")

GROUP_ID = int(os.getenv("GROUP_ID", "0"))

ADMIN_IDS = [
    int(x.strip())
    for x in os.getenv("ADMIN_IDS", "").split(",")
    if x.strip()
]

# ==========================
# АНТИСПАМ
# ==========================

DAILY_POST_LIMIT = 3

WARNING_LIMIT = 3

BLOCK_HOURS = 24

MIN_TEXT_LENGTH = 10

MAX_TEXT_LENGTH = 5000

POST_COOLDOWN_MINUTES = 5

BLACKLIST_KEYWORDS = [
    "спам",
    "реклама",
    "http://",
    "https://"
]

# ==========================
# БД
# ==========================

DB_NAME = "bot_posts.db"

OWNER_ID = -GROUP_ID
