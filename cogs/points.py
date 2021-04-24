import discord
from discord.ext import commands
from time import time

from helper import get_user_data, save_user_data, get_guild_data

class cog(commands.Cog):
    def __init__(self, client):
        self.client = client

    @commands.command()
    async def points(self, context, member: discord.Member = None):
        if not member:
            member = context.author

        try:
            user_data = get_user_data(member.id)
            points = user_data["points"]
            await context.send(f"{points} points")
        except Exception as error_message:
            await context.send(error_message)

    @commands.command()
    async def setpoints(self, context, member: discord.Member, amount: int):
        try:
            user_data = get_user_data(member.id)
            user_data["points"] = amount
            save_user_data(user_data)
            await context.send(f"Set {member}'s points to {amount}")
        except Exception as error_message:
            await context.send(error_message)

    @commands.command()
    async def addpoints(self, context, member: discord.Member, amount: int):
        try:
            if amount <= 0:
                await context.send(f"{amount} is not greater than 0")
                return

            user_data = get_user_data(member.id)
            user_data["points"] += amount
            save_user_data(user_data)
            await context.send(f"Gave {amount} points to {member}")
        except Exception as error_message:
            await context.send(error_message)

    @commands.command()
    async def daily(self, context):
        try:
            guild_data = get_guild_data(context.guild.id)
            user_data = get_user_data(context.author.id)

            seconds_in_a_day = 60 * 60 * 24
            if user_data["claimed_daily_reward_time"] and time() - user_data["claimed_daily_reward_time"] < seconds_in_a_day:
                hours_to_wait = round((seconds_in_a_day - (time() - user_data["claimed_daily_reward_time"])) / 60 / 60)
                await context.send(f"You must wait {hours_to_wait} hour(s) to claim your daily reward")
                return

            daily_reward = guild_data["daily_reward"]
            user_data["points"] += daily_reward
            user_data["claimed_daily_reward_time"] = time()
            save_user_data(user_data)
            await context.send(f"You claimed your daily reward and earned {daily_reward} points!")
        except Exception as error_message:
            await context.send(error_message)

def setup(client):
    client.add_cog(cog(client))