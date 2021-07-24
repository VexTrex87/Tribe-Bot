import discord
from discord.ext import commands, tasks
import aiohttp
import random

from helper import create_embed, get_user_data, save_user_data, get_all_guild_data, get_all_user_data, wait_for_message, wait_for_reaction
from constants import GROUP_INFO_URL, USER_GROUPS_URL, USER_INFO_URL, USER_STATUS_URL, USERS_URL, ROBLOX_KEYWORD_COUNT, ROBLOX_KEYWORDS, ACCEPT_EMOJI, GROUPS_UPDATE_DELAY, REQUESTS_CHANNEL, GAMES_UPDATE_DELAY, CHANGE_EMOJI

async def get_group_name(group_id: int):
    url = GROUP_INFO_URL.replace('GROUP_ID', str(group_id))
    async with aiohttp.ClientSession() as session:
        async with session.get(url) as response:
            if response.status == 200:
                response_data = await response.json()
                return response_data.get('name')

async def get_user_groups(user_id: int):
    url = USER_GROUPS_URL.replace('USER_ID', str(user_id))
    groups = []
    async with aiohttp.ClientSession() as session:
        async with session.get(url) as response:
            if response.status == 200:
                response_data = await response.json()
                for group_info in response_data['data']:
                    group_id = group_info['group']['id']
                    groups.append(group_id)
                return groups

async def get_username(user_id: int):
    url = USER_INFO_URL.replace('USER_ID', str(user_id))
    async with aiohttp.ClientSession() as session:
        async with session.get(url) as response:
            if response.status == 200:
                response_data = await response.json()
                return response_data['name']

async def get_user_id(username: str):
    data = {'usernames': [username], 'excludeBannedUsers': False}
    async with aiohttp.ClientSession() as session:
        async with session.post(USERS_URL, data = data) as response:
            if response.status == 200:
                response_data = await response.json()
                user = response_data['data'][0]
                if not user:
                    return None
                return user['id']

async def get_user_description(user_id: int):
    url = USER_INFO_URL.replace('USER_ID', str(user_id))
    async with aiohttp.ClientSession() as session:
        async with session.get(url) as response:
            if response.status == 200:
                response_data = await response.json()
                return response_data['description']

async def get_user_status(user_id: int):
    url = USER_STATUS_URL.replace('USER_ID', str(user_id))
    async with aiohttp.ClientSession() as session:
        async with session.get(url) as response:
            if response.status == 200:
                response_data = await response.json()
                return response_data['status']

def generate_random_keywords():
    random_keywords = random.sample(ROBLOX_KEYWORDS, ROBLOX_KEYWORD_COUNT)
    return ' '.join(random_keywords)

class roblox(commands.Cog):
    def __init__(self, client):
        self.client = client
        self.players = {}
        self.check_groups.start()
        self.check_games.start()

    def cog_unload(self):
        self.check_groups.cancel()
        self.check_games.cancel()

    def cog_load(self):
        self.check_groups.start()
        self.check_games.start()

    @tasks.loop(seconds = GROUPS_UPDATE_DELAY)
    async def check_groups(self):
        await self.client.wait_until_ready()

        # loop through each guild
        for guild_data in get_all_guild_data():
            # check if guild exists
            guild = self.client.get_guild(guild_data['guild_id'])
            if not guild:
                continue

            # get guild's roblox groups
            groups = guild_data['roblox_groups']
            if not groups or len(groups) == 0:
                continue

            # loop through each user in guild
            for user_data in get_all_user_data():
                # check if user exists
                user = guild.get_member(user_data['user_id'])
                if not user:
                    continue

                # check if roblox user exists
                roblox_user_id = user_data.get('roblox_account_id')
                if not roblox_user_id:
                    continue

                # get user's groups
                user_groups = await get_user_groups(roblox_user_id)
                if not user_groups or len(user_groups) == 0:
                    continue

                # loop through each group
                for user_group_id in user_groups:
                    # check if user's group is a valid guild group
                    if not user_group_id in groups:
                        continue
                    
                    if user_group_id in user_data['roblox_groups']:
                        continue

                    # check if group exists
                    group_name = await get_group_name(user_group_id)
                    if not group_name:
                        continue

                    # award user
                    user_data['points'] += guild_data['group_award']
                    user_data['roblox_groups'].append(user_group_id)

                    try:
                        await user.send(embed = create_embed({
                            'title': 'You earned {} points for joining {}'.format(guild_data['group_award'], group_name),
                        }))
                    except discord.Forbidden:
                        print('Cannot tell {} that they earned {} points for joining roblox group {}'.format(user, guild_data['group_award'], group_name))

                save_user_data(user_data)

    @tasks.loop(seconds = GAMES_UPDATE_DELAY)
    async def check_games(self):
        await self.client.wait_until_ready()

        # loop through each guild
        for guild_data in get_all_guild_data():
            # check if guild exists
            guild = self.client.get_guild(guild_data['guild_id'])
            if not guild:
                continue

            # go through each guild user
            for user in guild.members:
                user_data = get_user_data(user.id)

                # check if user has a roblox account
                roblox_user_id = user_data['roblox_account_id']
                if not roblox_user_id:
                    continue

                if not await get_username(roblox_user_id):
                    continue

                # check if user is playing a game
                for game_id, player_ids in self.players.items():
                    if str(roblox_user_id) in player_ids:
                        # check if game is a guild game
                        if int(game_id) in guild_data['roblox_games']:
                            user_data['points'] += guild_data['game_award']
                            print('Gave {} {} points for playing {}'.format(user, guild_data['game_award'], game_id))
                            break

                save_user_data(user_data)

    @commands.Cog.listener()
    async def on_message(self, message):
        if not message.guild or message.channel.id != REQUESTS_CHANNEL or not message.author.bot:
            return

        fields = message.content.split('/')
        status = fields[0].split('=')[1]
        player_id = fields[1].split('=')[1]
        place_id = fields[2].split('=')[1]

        if status == 'player_joined':
            if not self.players.get(place_id):
                self.players[place_id] = [player_id]
            else:
                self.players[place_id].append(player_id)
        elif status == 'player_left':
            if self.players.get(place_id) and player_id in self.players[place_id]:
                self.players[place_id].remove(player_id)
                if len(self.players[place_id]) == 0:
                    self.players.pop(place_id)

    @commands.command()
    async def link(self, context):
        response = await context.send(embed = create_embed({
            'title': f'Retrieving your roblox account...',
            'color': discord.Color.gold()
        }))

        try:
            # get roblox account
            user_data = get_user_data(context.author.id)
            roblox_account_id = user_data['roblox_account_id']
            roblox_account_username = roblox_account_id and await get_username(roblox_account_id)
            await response.add_reaction(CHANGE_EMOJI)
            await response.edit(embed = create_embed({
                'title': roblox_account_username and f'Your your roblox account is {roblox_account_username}' or 'You do not have a linked roblox account',
                'description': f'React with {CHANGE_EMOJI} to link a new roblox account'
            }))

            # change roblox account
            reaction, user = await self.wait_for_reaction(self.client, context, CHANGE_EMOJI)
            if not reaction:
                await response.edit(embed = create_embed({
                    'title': roblox_account_username and f'Your your roblox account is {roblox_account_username}' or 'You do not have a linked roblox account',
                }))
                return

            # get user id
            if context.guild:
                await response.clear_reactions()
                await response.edit(embed = create_embed({
                    'title': 'Enter your roblox username',
                    'color': discord.Color.gold()
                }))
            else:
                response = await context.send(embed = create_embed({
                    'title': 'Enter your roblox username',
                    'color': discord.Color.gold()
                }))

            message = await wait_for_message(self.client, context)
            if not message:
                await response.edit(embed = create_embed({
                    'title': 'No response sent',
                    'color': discord.Color.red()
                }))
                return

            if context.guild:
                await message.delete()

            username = message.content
            user_id = await get_user_id(username)
            if not user_id:
                await response.edit(embed = create_embed({
                    'title': f'Could not retrieve roblox user {username}',
                    'color': discord.Color.red()
                }))
                return

            # wait for verification text
            verification_message = generate_random_keywords()
            await response.add_reaction(ACCEPT_EMOJI)
            await response.edit(embed = create_embed({
                'title': f'Change your user description or status to the following text. React with {ACCEPT_EMOJI} when done',
                'color': discord.Color.gold()
            }, {
                'Text': verification_message
            }))

            reaction, user = await wait_for_reaction(self.client, context, ACCEPT_EMOJI, timeout=300)
            if not reaction:
                await response.edit(embed = create_embed({
                    'title': 'No response sent',
                    'color': discord.Color.red()
                }))
                return

            if context.guild:
                await response.clear_reactions()

            is_verified = verification_message in await get_user_description(user_id) or verification_message in await get_user_status(user_id)
            if is_verified:
                user_data['roblox_account_id'] = user_id
                save_user_data(user_data)

                await response.edit(embed = create_embed({
                    'title': f'Linked discord account {context.author} to roblox account {username}',
                    'color': discord.Color.green()
                }))
            else:
                await response.edit(embed = create_embed({
                    'title': f'Could not find verification message in {username}\'s status or description',
                    'color': discord.Color.red()
                }))
        except Exception as error_message:
            import traceback
            traceback.print_exc()

            await response.edit(embed = create_embed({
                'title': f'Could not retrieve your roblox account',
                'color': discord.Color.red()
            }, {
                'Error Message': error_message
            }))

def setup(client):
    client.add_cog(roblox(client))
