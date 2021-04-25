EXTENSIONS = [
    "events",
    "bot",
    "default",
    "points",
    "giveaway"
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
    "points_per_aotd": 50,
    "giveaway_channel": None,
    "giveaways": [],
}

DEFAULT_USER_DATA = {
    "user_id": None,
    "points": 0,
    "claimed_daily_reward_time": None,
    "answered_qotd": False,
}

QOTD_TAG = "QOTD"
GIVEAWAY_UPDATE_DELAY = 1
GIVEAWAY_ENTRY_COST = 1