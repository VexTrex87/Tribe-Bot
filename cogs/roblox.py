import discord
from discord.ext import commands, tasks
import aiohttp
import random
import asyncio

from helper import create_embed, convert_dictionary_to_tree, get_user_data, save_user_data, get_all_guild_data, get_all_user_data
from constants import GROUP_INFO_URL, USER_GROUPS_URL, USER_INFO_URL, USER_STATUS_URL, USERS_URL, ROBLOX_KEYWORD_COUNT, ROBLOX_KEYWORDS, ACCEPT_EMOJI, GROUPS_UPDATE_DELAY

async def get_group_name(group_id: int):
    url = GROUP_INFO_URL.replace("GROUP_ID", str(group_id))
    async with aiohttp.ClientSession() as session:
        async with session.get(url) as response:
            if response.status == 200:
                response_data = await response.json()
                return response_data.get("name")

async def get_user_groups(user_id: int):
    url = USER_GROUPS_URL.replace("USER_ID", str(user_id))
    groups = []
    async with aiohttp.ClientSession() as session:
        async with session.get(url) as response:
            if response.status == 200:
                response_data = await response.json()
                for group_info in response_data["data"]:
                    group_id = group_info["group"]["id"]
                    groups.append(group_id)
                return groups

async def get_username(user_id: int):
    url = USER_INFO_URL.replace("USER_ID", str(user_id))
    async with aiohttp.ClientSession() as session:
        async with session.get(url) as response:
            if response.status == 200:
                response_data = await response.json()
                return response_data["name"]

async def get_user_id(username: str):
    data = {"usernames": [username], "excludeBannedUsers": False}
    async with aiohttp.ClientSession() as session:
        async with session.post(USERS_URL, data = data) as response:
            if response.status == 200:
                response_data = await response.json()
                user = response_data["data"][0]
                if not user:
                    return None
                return user["id"]

async def get_user_description(user_id: int):
    url = USER_INFO_URL.replace("USER_ID", str(user_id))
    async with aiohttp.ClientSession() as session:
        async with session.get(url) as response:
            if response.status == 200:
                response_data = await response.json()
                return response_data["description"]

async def get_user_status(user_id: int):
    url = USER_STATUS_URL.replace("USER_ID", str(user_id))
    async with aiohttp.ClientSession() as session:
        async with session.get(url) as response:
            if response.status == 200:
                response_data = await response.json()
                return response_data["status"]

def generate_random_keywords():
    random_keywords = random.sample(ROBLOX_KEYWORDS, ROBLOX_KEYWORD_COUNT)
    return " ".join(random_keywords)

class roblox(commands.Cog):
    def __init__(self, client):
        self.client = client
        self.check_groups.start()

    def cog_unload(self):
        self.check_groups.cancel()

    def cog_load(self):
        self.check_groups.start()

    @tasks.loop(seconds = GROUPS_UPDATE_DELAY)
    async def check_groups(self):
        await self.client.wait_until_ready()

        # loop through each guild
        for guild_data in get_all_guild_data():
            # check if guild exists
            guild = self.client.get_guild(guild_data["guild_id"])
            if not guild:
                continue

            # get guild's roblox groups
            groups = guild_data["roblox_groups"]
            if not groups or len(groups) == 0:
                continue

            # loop through each user in guild
            for user_data in get_all_user_data():
                # check if user exists
                user = await guild.fetch_member(user_data["user_id"])
                if not user:
                    continue

                # check if roblox user exists
                roblox_user_id = user_data.get("roblox_account_id")
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

                    # check if user has already been awared for joining this group
                    if user_group_id in user_data["roblox_groups"]:
                        continue

                    # check if group exists
                    group_name = await get_group_name(user_group_id)
                    if not group_name:
                        continue

                    # award user
                    user_data["points"] += guild_data["group_award"]
                    user_data["roblox_groups"].append(user_group_id)
                    save_user_data(user_data)

                    await user.send(embed = create_embed({
                        "title": "You earned {} points for joining {}".format(guild_data["group_award"], group_name),
                    }))

    @commands.command()
    @commands.guild_only()
    async def linkroblox(self, context, *, username: str):
        response = await context.send(embed = create_embed({
            "title": f"Linking roblox account {username}...",
            "color": discord.Color.gold()
        }))

        try:
            user_id = await get_user_id(username)
            if not user_id:
                await response.edit(embed = create_embed({
                    "title": f"Could not retrieve roblox user {username}",
                    "color": discord.Color.red()
                }))
                return

            verification_message = generate_random_keywords()
            await response.edit(embed = create_embed({
                "title": "Change your user description or status to the following text. Say \"done\" when finished. Timeout in 30 seconds.",
                "color": discord.Color.gold()
            }, {
                "Text": verification_message
            }))

            def check_response(reaction, user):
                return not user.bot and user == context.author and str(reaction.emoji) == ACCEPT_EMOJI and reaction.message.channel == context.channel

            try:
                await response.add_reaction(ACCEPT_EMOJI)
                reaction, user = await self.client.wait_for("reaction_add", check = check_response, timeout = 30)
            except asyncio.TimeoutError:
                await response.edit(embed = create_embed({
                    "title": f"No response sent in time to verify roblox account {username}",
                    "color": discord.Color.red()
                }))
                return
            else:
                is_verified = verification_message in await get_user_description(user_id) or verification_message in await get_user_status(user_id)
                if is_verified:
                    user_data = get_user_data(context.author.id)
                    user_data["roblox_account_id"] = user_id
                    save_user_data(user_data)

                    await response.edit(embed = create_embed({
                        "title": f"Linked discord account {context.author} to roblox account {username}",
                        "color": discord.Color.green()
                    }))
                else:
                    await response.edit(embed = create_embed({
                        "title": f"Could not find verification message in {username}'s status or description",
                        "color": discord.Color.red()
                    }))

        except Exception as error_message:
            create_embed({
                "title": f"Could not link roblox account {username}",
                "color": discord.Color.red()
            }, {
                "Error Message": error_message
            })

    @commands.command()
    @commands.guild_only()
    async def robloxaccount(self, context, member: discord.Member = None):
        if not member:
            member = context.author

        response = await context.send(embed = create_embed({
            "title": f"Loading {member}'s roblox account'...",
            "color": discord.Color.gold()
        }))

        try:
            user_data = get_user_data(member.id)
            user_id = user_data.get("roblox_account_id")
            if not user_id:
                await response.edit(embed = create_embed({
                    "title": f"{member} has no linked roblox account",
                    "color": discord.Color.red()
                }))
                return

            username = await get_username(user_id)
            if not username:
                await response.edit(embed = create_embed({
                    "title": f"Could not get the username of roblox account {user_id}",
                    "color": discord.Color.red()
                }))
                return

            await response.edit(embed = create_embed({
                "title": f"{member}'s roblox account is {username}",
                "color": discord.Color.green()
            }))
        except Exception as error_message:
            await response.edit(embed = create_embed({
                "title": f"Could not load {member}'s roblox account",
                "color": discord.Color.red()
            }, {
                "Error Message": error_message
            }))

def setup(client):
    client.add_cog(roblox(client))