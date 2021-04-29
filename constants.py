EXTENSIONS = [
    "events",
    "bot",
    "default",
    "points",
    "giveaway",
    "roblox"
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
    "roblox_groups": [],
    "group_award": 500,
}

DEFAULT_USER_DATA = {
    "user_id": None,
    "points": 0,
    "claimed_daily_reward_time": None,
    "answered_qotd": False,
    "roblox_account_id": None,
    "roblox_groups": []
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

GROUP_INFO_URL = "https://groups.roblox.com/v1/groups/GROUP_ID"
USER_GROUPS_URL = "https://groups.roblox.com/v2/users/USER_ID/groups/roles"
USER_INFO_URL = "https://users.roblox.com/v1/users/USER_ID"
USER_STATUS_URL = "https://users.roblox.com/v1/users/USER_ID/status"
USERS_URL = "https://users.roblox.com/v1/usernames/users"

ROBLOX_KEYWORD_COUNT = 5
ROBLOX_KEYWORDS = [
    "apple",
    "avocado",
    "almond",
    "bacon",
    "beef",
    "berry",
    "bread",
    "burrito",
    "cake",
    "caramel",
    "cereal",
    "cheese",
    "chicken",
    "chocolate",
    "cupcake",
    "candy",
    "chips",
    "coffee",
    "doughnut",
    "egg",
    "grape",
    "honey",
    "ham",
    "hamburger",
    "jelly",
    "juice",
    "kiwi",
    "lemon",
    "muffin",
    "milk",
    "oatmeal",
    "peach",
    "pear",
    "pineapple",
    "pizza",
    "pie",
    "sandwich",
    "taco",
    "waffle",
    "water",
    "yogurt",
]
ACCEPT_EMOJI = "✅"
GROUPS_UPDATE_DELAY = 60

REQUESTS_CHANNEL = 834455396667359242