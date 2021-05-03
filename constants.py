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
    "roblox_games": [],
    "game_award": 10,
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

SETTINGS = {
    "prefix <new_prefix: string>": "Changes the bot's prefix for the guild.",
    "daily_reward <points: integer>": "Changes the amount of points members get for running the daily command.",
    "point_channels <channel_name: string / channel_id: integer / channel_mention: mention>": "Adds/removes the channels that members can earn points for chatting.",
    "points_per_message <points: integer>": "Changes the amount of points members get for sending messages in verified point channels.",
    "message_cooldown <seconds: integer>": "Changes the cooldown delay for members earnings points from chatting.",
    "qotd_channel <channel_name: string / channel_id: integer / channel_mention: mention>": "Changes the channel where QOTD messages are sent and detected.",
    "aotd_keywords <keyword: string>": "Adds/removes the keywords that will be detected to reward members points for answering the QOTD.",
    "points_per_aotd <points: intenger>": "Changes the amount of points members will get for answering the QOTD.",
    "giveaway_channel <channel_name: string / channel_id: integer / channel_mention: mention>": "Changes the channel where giveaways will be announced.",
    "giveaway_entry_cost <points: intenger>": "The amount of points that will be detected from a member for entering a giveaway.",
    "roblox_groups <group_id: integer>": "Adds/removes the groups members will be rewarded if they join it.",
    "group_award <points: integer>": "Changes the amount of points members will get for joining a verified roblox group.",
    "roblox_games <game_id: intenger>": "Adds/removes the games members will e rewarded if they play it every interval set by the guild.",
    "game_award <points: integer>": "Changes the amount of points members will get for playing a verified roblox game..",
}

COMMANDS = {
    "Default Commands": {
        "help": "Retrieves bot commands.",
        "info": "Retrieves the bot's ping, invite link, uptime, number of servers, and number of users.",
        "settings": "Retrieves and changes the guild's settings.",
        "restart": "Restarts the bot.",
    },
    "Fun Commands": {
        "giveaway": "Creates a giveaway.",
        "points": "Loads a user's points.",
        "setpoints": "Changes a user's points.",
        "givepoints": "Adds a user's points.",
        "daily": "Gives the member free points. Can only be used once a day.",
        "link": "Links a user's Discord account to their Discord account.",
    }
}

PREFIX = "?"
MAX_LEADERBOARD_FIELDS = 10
CLIENT_ID = 834455533423427584
ACCEPT_EMOJI = "✅"
NEXT_EMOJI = "▶️"
BACK_EMOJI = "◀️"
CHANGE_EMOJI = "⚙️"
WAIT_DELAY = 5

GIVEAWAY_UPDATE_DELAY = 10

GROUP_INFO_URL = "https://groups.roblox.com/v1/groups/GROUP_ID"
USER_GROUPS_URL = "https://groups.roblox.com/v2/users/USER_ID/groups/roles"
USER_INFO_URL = "https://users.roblox.com/v1/users/USER_ID"
USER_STATUS_URL = "https://users.roblox.com/v1/users/USER_ID/status"
USERS_URL = "https://users.roblox.com/v1/usernames/users"
GROUPS_UPDATE_DELAY = 60
GAMES_UPDATE_DELAY = 15
REQUESTS_CHANNEL = 834455396667359242
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
