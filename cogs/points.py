import discord
from discord.ext import commands

from helper import get_user_data, save_user_data

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

def setup(client):
    client.add_cog(cog(client))