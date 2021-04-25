import discord
from discord.ext import commands
import os
import sys

from helper import create_embed

class bot(commands.Cog):
    def __init__(self, client):
        self.client = client

    @commands.command()
    @commands.check_any(commands.is_owner(), commands.has_permissions(administrator = True))
    @commands.guild_only()
    async def run(self, context, *, code):
        response = await context.send(embed = create_embed({
            "title": f"Running code...",
            "color": discord.Color.gold()
        }, {
            "Code": code
        }))
        
        try:
            exec(code)
            await response.edit(embed = create_embed({
                "title": f"Ran code",
                "color": discord.Color.green()
            }, {
                "Code": code
            }))
        except Exception as error_message:
            await response.edit(embed = create_embed({
                "title": f"Could not run code",
                "color": discord.Color.red()
            }, {
                "Error Message": error_message,
                "Code": code
            }))
        
    @commands.command()
    @commands.check_any(commands.is_owner(), commands.has_permissions(administrator = True))
    @commands.guild_only()
    async def cls(self, context):
        response = await context.send(embed = create_embed({
            "title": f"Clearing terminal...",
            "color": discord.Color.gold()
        }))
        
        try:
            os.system("cls" if os.name == "nt" else "clear")
            await response.edit(embed = create_embed({
                "title": f"Terminal cleared",
                "color": discord.Color.green()
            }))
        except Exception as error_message:
            await response.edit(embed = create_embed({
                "title": f"Could not clear terminal",
                "color": discord.Color.red()
            }, {
                "Error Message": error_message,
            }))
            
    @commands.command()
    @commands.check_any(commands.is_owner(), commands.has_permissions(administrator = True))
    @commands.guild_only()
    async def shutdown(self, context):
        response = await context.send(embed = create_embed({
            "title": f"Shutting down...",
            "color": discord.Color.gold()
        }))
        
        sys.exit()

def setup(client):
    client.add_cog(bot(client))