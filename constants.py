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
    "aotd_keywords": ["qotd", "aotd"],
    "points_per_aotd": 50,
    "giveaway_channel": None,
    "giveaway_entry_cost": 1,
}

DEFAULT_USER_DATA = {
    "user_id": None,
    "points": 0,
    "claimed_daily_reward_time": None,
    "answered_qotd": False,
}

DEFAULT_GIVEAWAYS_DATA = {
    "title": "",
    "prize": 0,
    "creator": None,
    "endsin": None,
    "join_emoji": None,
    "guild_id": None,
    "message_id": None,
    "member_pool": []
}

GIVEAWAY_UPDATE_DELAY = 10
PREFIX = "?"
MAX_LEADERBOARD_FIELDS = 10