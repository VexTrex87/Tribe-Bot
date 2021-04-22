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
}

DEFAULT_USER_DATA = {
    "user_id": None,
    "points": 0,
    "claimed_daily_reward_time": None,
}