import discord

EXTENSIONS = [
    'bot',
    'default',
    'events',
    'fun',
    'giveaway',
    'points',
    'roblox'
]

DEFAULT_GUILD_DATA = {
    'guild_id': None,
    'prefix': '?',
    'bot_manager': None,
    'giveaway_manager': None,
    'daily_reward': 10,
    'point_channels': [],
    'points_per_message': 1,
    'message_cooldown': 10,
    'qotd_channel': None,
    'aotd_keywords': ['qotd', 'aotd'],
    'points_per_aotd': 50,
    'giveaway_channel': None,
    'suggestion_channel': None,
    'roblox_groups': [],
    'group_award': 500,
    'roblox_games': [],
    'game_award': 10,
}

DEFAULT_USER_DATA = {
    'user_id': None,
    'points': 0,
    'claimed_daily_reward_time': None,
    'answered_qotd': False,
    'roblox_account_id': None,
    'roblox_groups': []
}

DEFAULT_GIVEAWAYS_DATA = {
    'title': '',
    'price': 0,
    'reward': 0,
    'endsin': None,
    'join_emoji': None,
    'creator': None,
    'guild_id': None,
    'message_id': None,
    'member_pool': []
}

COMMANDS = {
    'Default Commands': {
        'help': 'Retrieves bot commands.',
        'info': 'Retrieves the bot\'s ping, invite link, uptime, number of servers, and number of users.',
        'settings': 'Retrieves and changes the guild\'s settings.',
        'restart': 'Restarts the bot.',
    },
    'Fun Commands': {
        '8ball <question>' : 'Responds with a random yes/no type answer.',
        'giveaway': 'Creates a giveaway.',
        'points': 'Loads a user\'s points.',
        'setpoints': 'Changes a user\'s points.',
        'addpoints': 'Adds a user\'s points.',
        'daily': 'Gives the member their daily reward of points. Can only be used once a day.',
        'leaderboard': 'Retrieves the users with the most points in the server.',
        'link': 'Links a user\'s Discord account to their Roblox account.',
    }
}

EIGHTBALL_RESPONSES = [
    'It is certain.',
    'It is decidedly so.',
    'Without a doubt.',
    'Yes - definitely.',
    'You may rely on it.',
    'As I see it, yes.',
    'Most likely.',
    'Outlook good.',
    'Yes.',
    'Signs point to yes.',
    'Reply hazy, try again.',
    'Ask again later.',
    'Better not tell you now.',
    'Cannot predict now.',
    'Concentrate and ask again.',
    'Don\'t count on it.',
    'My reply is no.',
    'My sources say no.',
    'Outlook not so good.',
    'Very doubtful.',
    'No.',
    'Your question isn\'t important, but btc to the moon is.',
    'Ask better questions next time.',
]

ROBLOX_KEYWORDS = [
    'apple',
    'avocado',
    'almond',
    'bacon',
    'beef',
    'berry',
    'bread',
    'burrito',
    'cake',
    'caramel',
    'cereal',
    'cheese',
    'chicken',
    'chocolate',
    'cupcake',
    'candy',
    'chips',
    'coffee',
    'doughnut',
    'egg',
    'grape',
    'honey',
    'ham',
    'hamburger',
    'jelly',
    'juice',
    'kiwi',
    'lemon',
    'muffin',
    'milk',
    'oatmeal',
    'peach',
    'pear',
    'pineapple',
    'pizza',
    'pie',
    'sandwich',
    'taco',
    'waffle',
    'water',
    'yogurt',
]

SUPPORTED_COLORS = {
    'teal': discord.Color.teal(),
	'dark_teal': discord.Color.dark_teal(),
	'green': discord.Color.green(),
	'dark_green': discord.Color.dark_green(),
	'blue': discord.Color.blue(),
	'dark_blue': discord.Color.dark_blue(),
	'purple': discord.Color.purple(),
	'dark_purple': discord.Color.dark_purple(),
	'magenta': discord.Color.magenta(),
	'dark_magenta': discord.Color.dark_magenta(),
	'gold': discord.Color.gold(),
	'dark_gold': discord.Color.dark_gold(),
	'orange': discord.Color.orange(),
	'dark_orange': discord.Color.dark_orange(),
	'red': discord.Color.red(),
	'dark_red': discord.Color.dark_red(),
	'lighter_grey': discord.Color.lighter_grey(),
	'lighter_gray': discord.Color.lighter_gray(),
	'dark_grey': discord.Color.dark_grey(),
	'dark_gray': discord.Color.dark_gray(),
	'light_grey': discord.Color.light_grey(),
	'light_gray': discord.Color.light_gray(),
	'darker_grey': discord.Color.darker_grey(),
	'darker_gray': discord.Color.darker_gray(),
	'blurple': discord.Color.blurple(),
	'greyple': discord.Color.greyple(),
	'dark_theme': discord.Color.dark_theme(),
}

DEFAULT_ACTIVITY = '?help'
PRODUCTION_DATABASE = 'database1'
DEBUG_DATABASE = 'database2'
CLIENT_ID = 834455533423427584

ACCEPT_EMOJI = '✅'
DECLINE_EMOJI = '❌'
NEXT_EMOJI = '▶️'
BACK_EMOJI = '◀️'
THUMBS_UP = '👍'
THUMBS_DOWN = '👎'
CHANGE_EMOJI = '⚙️'

GROUP_INFO_URL = 'https://groups.roblox.com/v1/groups/GROUP_ID'
USER_GROUPS_URL = 'https://groups.roblox.com/v2/users/USER_ID/groups/roles'
USER_INFO_URL = 'https://users.roblox.com/v1/users/USER_ID'
USER_STATUS_URL = 'https://users.roblox.com/v1/users/USER_ID/status'
USERS_URL = 'https://users.roblox.com/v1/usernames/users'
COLOR_PALETTE = 'https://gyazo.com/86b4659a58c771689d464d5bbd01fc3e'

TEST_IMAGE_PATH = 'assets/test_image.png'
TEST_IMAGE_SHORT_PATH = 'test_image.png'
TEST_THUMBNAIL_PATH = 'assets/test_thumbnail.png'
TEST_THUMBNAIL_SHORT_PATH = 'test_thumbnail.png'

MAX_LEADERBOARD_FIELDS = 10
WAIT_DELAY = 3
GIVEAWAY_UPDATE_DELAY = 10
GROUPS_UPDATE_DELAY = 60
GAMES_UPDATE_DELAY = 15
REQUESTS_CHANNEL = 834455396667359242
ROBLOX_KEYWORD_COUNT = 5
