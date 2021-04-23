PREFIX = "?"
EXTENSIONS = [
    "events",
    "bot",
    "default",
    "points"
]

DEFAULT_GUILD_DATA = {
    "guild_id": None,
    "prefix": "?",
    "daily_reward": 10,
    "point_channels": [],
    "points_per_message": 1,
    "message_cooldown": 10,
    "qotd_channel": None,
    "aotd_channel": None,
    "points_per_aotd": 50
}

DEFAULT_USER_DATA = {
    "user_id": None,
    "points": 0,
    "claimed_daily_reward_time": None,
    "answered_qotd": False,
}

QOTD_TAG = "QOTD"