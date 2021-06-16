import discord
from discord.ext import commands
import os
import sys
import asyncio
from helper import create_embed, check_if_bot_manager, wait_for_reaction
from constants import ACCEPT_EMOJI

class bot(commands.Cog, description = "Commands for managing the bot."):
    def __init__(self, client):
        self.client = client

    @commands.command()
    @commands.check_any(commands.is_owner(), commands.check(check_if_bot_manager))
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
    @commands.check_any(commands.is_owner(), commands.check(check_if_bot_manager))
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
    @commands.check_any(commands.is_owner(), commands.check(check_if_bot_manager))
    async def restart(self, context):
        response = await context.send(embed = create_embed({
            "title": f"Are you sure you want to restart the bot?",
            "color": discord.Color.gold()
        }))
        
        try:
            await response.add_reaction(ACCEPT_EMOJI)
            reaction, user = await wait_for_reaction(self.client, context, ACCEPT_EMOJI)
            if not reaction:
                await response.edit(embed=create_embed({
                    "title": "Restart canceled",
                    "color": discord.Color.red()
                }))
                return

            await response.edit(embed = create_embed({
                "title": "Restarting bot...",
                "color": discord.Color.green()
            }))

            sys.exit()
        except Exception as error_message:
            await response.edit(embed=create_embed({
                "title": "Could not restart bot",
                "color": discord.Color.red()
            }, {
                "Error Message": error_message
            }))

def setup(client):
    client.add_cog(bot(client))
