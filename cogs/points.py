import discord
from discord.ext import commands
from time import time

from helper import get_user_data, save_user_data, get_guild_data, create_embed

class points(commands.Cog):
    def __init__(self, client):
        self.client = client

    @commands.command()
    @commands.guild_only()
    async def points(self, context, member: discord.Member = None):
        if not member:
            member = context.author

        response = await context.send(embed = create_embed({
            "title": f"Loading points for {member}...",
            "color": discord.Color.gold()
        }))
        
        try:
            user_data = get_user_data(member.id)
            points = user_data["points"]
            await response.edit(embed = create_embed({
                "title": f"{points} points",
            }))
        except Exception as error_message:
            await response.edit(embed = create_embed({
                "title": f"Could not load {member}'s points",
                "color": discord.Color.red()
            }, {
                "Error Message": error_message
            }))
            
    @commands.command()
    @commands.check_any(commands.is_owner(), commands.has_permissions(administrator = True))
    @commands.guild_only()
    async def setpoints(self, context, member: discord.Member, amount: int):
        response = await context.send(embed = create_embed({
            "title": f"Changing {member}'s points to {amount}...",
            "color": discord.Color.gold()
        }))
        
        try:
            user_data = get_user_data(member.id) 
            user_data["points"] = amount
            save_user_data(user_data)

            await response.edit(embed = create_embed({
                "title": f"Set {member}'s points to {amount}",
                "color": discord.Color.green()
            }))
        except Exception as error_message:
            await response.edit(embed = create_embed({
                "title": f"Could not set {member}'s points to {amount}",
                "color": discord.Color.red()
            }, {
                "Error Message": error_message
            }))
            
    @commands.command()
    @commands.check_any(commands.is_owner(), commands.has_permissions(administrator = True))
    @commands.guild_only()
    async def addpoints(self, context, member: discord.Member, amount: int):
        response = await context.send(embed = create_embed({
            "title": f"Adding {amount} points to {member}...",
            "color": discord.Color.gold()
        }))
        
        try:
            if amount <= 0:
                await response.edit(embed = create_embed({
                    "title": f"{amount} is not greater than 0",
                    "color": discord.Color.red()
                }))
                return

            user_data = get_user_data(member.id)
            user_data["points"] += amount
            save_user_data(user_data)
            
            await response.edit(embed = create_embed({
                "title": f"Gave {amount} points to {member}",
                "color": discord.Color.green()
            }))
        except Exception as error_message:
            await response.edit(embed = create_embed({
                "title": f"Could not give {amount} points to {member}",
                "color": discord.Color.red()
            }, {
                "Error Message": error_message
            }))
            
    @commands.command()
    @commands.guild_only()
    async def daily(self, context):
        response = await context.send(embed = create_embed({
            "title": f"Giving daily points...",
            "color": discord.Color.gold()
        }))
        
        try:
            guild_data = get_guild_data(context.guild.id)
            user_data = get_user_data(context.author.id)

            seconds_in_a_day = 60 * 60 * 24
            if user_data["claimed_daily_reward_time"] and time() - user_data["claimed_daily_reward_time"] < seconds_in_a_day:
                hours_to_wait = round((seconds_in_a_day - (time() - user_data["claimed_daily_reward_time"])) / 60 / 60)
                await response.edit(embed = create_embed({
                    "title": f"You must wait {hours_to_wait} hour(s) to claim your daily reward",
                    "color": discord.Color.red()
                }))
                return

            daily_reward = guild_data["daily_reward"]
            user_data["points"] += daily_reward
            user_data["claimed_daily_reward_time"] = time()
            save_user_data(user_data)

            await response.edit(embed = create_embed({
                "title": f"You claimed your daily reward and earned {daily_reward} points!",
                "color": discord.Color.green()
            }))
        except Exception as error_message:
            await response.edit(embed = create_embed({
                "title": f"Could not claim daily points",
                "color": discord.Color.red()
            }, {
                "Error Message": error_message
            }))
            
def setup(client):
    client.add_cog(points(client))