import discord
from discord.ext import commands
import time
import random

from helper import create_embed
from constants import EIGHTBALL_RESPONSES

class fun(commands.Cog):
    def __init__(self, client):
        self.client = client
        self.uptime = time.time()
 
    @commands.command(aliases = ['8ball'])
    async def eightball(self, context, *, question: str):
        response = await context.send(embed = create_embed({
            'title': 'Loading response...',
            'color': discord.Color.gold()   
        }))

        try:
            answer = random.choice(EIGHTBALL_RESPONSES)
            await response.edit(embed = create_embed({
                'title': answer
            }))
        except Exception as error_message:
            await response.edit(embed = create_embed({
                'title': 'Could not load response',
                'color': discord.Color.red()
            }, {
                'Error Message': error_message,
                'Question': question,
            }))

def setup(client):
    client.add_cog(fun(client))
