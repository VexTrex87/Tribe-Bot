import discord
from discord.ext import commands
import os
import sys

class events(commands.Cog, description = "Bot and server events."):
    def __init__(self, client):
        self.client = client

    @commands.command()
    async def run(self, context, *, code):
        try:
            exec(code)
            await context.send("Ran code")
        except Exception as error_message:
            await context.send(error_message)
        
    @commands.command()
    async def cls(self, context):
        try:
            os.system("cls" if os.name == "nt" else "clear")
            await context.send("Terminal cleared")
        except Exception as error_message:
            await context.send("Could not clear terminal")

    @commands.command()
    async def shutdown(self, context):
        await context.send("Restarting...")
        sys.exit()

def setup(client):
    client.add_cog(events(client))