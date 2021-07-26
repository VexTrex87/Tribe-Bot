import sys
import os
import dotenv

TOKEN = None
dotenv.load_dotenv('.env')
if len(sys.argv) > 1:
    if sys.argv[1] == '-d':
        print('Running in debug mode')
        TOKEN = os.getenv('DEBUG_TOKEN')
    elif sys.argv[1] == '-p':
        print('Running in production mode')
        TOKEN = os.getenv('PRODUCTION_TOKEN')
if not TOKEN:
    print('No run mode specified')
    sys.exit()

import discord
from discord.ext import commands
from constants import EXTENSIONS, DEFAULT_GUILD_DATA, DEFAULT_ACTIVITY
from helper import create_embed, get_guild_data

async def get_prefix(client, context):
    if context.guild:
        guild_data = get_guild_data(context.guild.id)
        return guild_data['prefix']
    else:
        return DEFAULT_GUILD_DATA['prefix']

intents = discord.Intents.default()
intents.members = True
client = commands.Bot(activity=discord.Game(name=DEFAULT_ACTIVITY), command_prefix=get_prefix, intents=intents, case_insensitive=True)

@client.command()
@commands.check_any(commands.is_owner(), commands.has_permissions(administrator = True))
async def load(context, extension: str):
    response = await context.send(embed = create_embed({
        'title': f'Loading {extension}...',
        'color': discord.Color.gold()
    }))

    try:
        client.load_extension(f'cogs.{extension}')
        await response.edit(embed = create_embed({
            'title': f'Loaded {extension}',
            'color': discord.Color.green()
        }))
    except Exception as error_message:
        await response.edit(embed = create_embed({
            'title': f'Could not load {extension}',
            'color': discord.Color.red()
        }, {
            'Error Message': error_message
        }))

@client.command()
@commands.check_any(commands.is_owner(), commands.has_permissions(administrator = True))
async def unload(context, extension: str):
    response = await context.send(embed = create_embed({
        'title': f'Unloading {extension}...',
        'color': discord.Color.gold()
    }))

    try:
        client.unload_extension(f'cogs.{extension}')
        await response.edit(embed = create_embed({
            'title': f'Unloaded {extension}',
            'color': discord.Color.green()
        }))
    except Exception as error_message:
        await response.edit(embed = create_embed({
            'title': f'Could not unload {extension}',
            'color': discord.Color.red()
        }, {
            'Error Message': error_message
        }))

@client.command()
async def reload(context, extension: str):
    response = await context.send(embed = create_embed({
        'title': f'Reloading {extension}...',
        'color': discord.Color.gold()
    }))

    try:
        client.reload_extension(f'cogs.{extension}')
        await response.edit(embed = create_embed({
            'title': f'Reloaded {extension}',
            'color': discord.Color.green()
        }))
    except Exception as error_message:
        await response.edit(embed = create_embed({
            'title': f'Could not reload {extension}',
            'color': discord.Color.red()
        }, {
            'Error Message': error_message
        }))

@client.command()
async def update(context):
    response = await context.send(embed = create_embed({
        'title': f'Updating bot...',
        'color': discord.Color.gold()
    }))

    try:
        for extension in EXTENSIONS:
            client.reload_extension(f'cogs.{extension}')
        await response.edit(embed = create_embed({
            'title': f'Updated bot',
            'color': discord.Color.green()
        }))
    except Exception as error_message:
        await response.edit(embed = create_embed({
            'title': f'Could not update bot',
            'color': discord.Color.red()
        }, {
            'Error Message': error_message
        }))

client.remove_command('help')

for extension in EXTENSIONS:
    client.load_extension(f'cogs.{extension}')

client.run(TOKEN)
