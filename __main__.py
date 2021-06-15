import discord
from discord.ext import commands
import os
from dotenv import load_dotenv
from constants import IS_TESTING, EXTENSIONS, PREFIX
from helper import create_embed, get_guild_data

async def get_prefix(client, context):
    if not context.guild:
        return PREFIX

    guild_data = get_guild_data(context.guild.id)
    return guild_data["prefix"]

load_dotenv('.vscode/.env')

TOKEN = os.getenv("TOKEN")
TEST_TOKEN = os.getenv("TEST_TOKEN")

intents = discord.Intents.default()
intents.members = True
client = commands.Bot(command_prefix = get_prefix, intents = intents)

@client.command()
@commands.check_any(commands.is_owner(), commands.has_permissions(administrator = True))
@commands.guild_only()
async def load(context, extension: str):
    response = await context.send(embed = create_embed({
        "title": f"Loading {extension}...",
        "color": discord.Color.gold()
    }))

    try:
        client.load_extension(f"cogs.{extension}")
        await response.edit(embed = create_embed({
            "title": f"Loaded {extension}",
            "color": discord.Color.green()
        }))
    except Exception as error_message:
        await response.edit(embed = create_embed({
            "title": f"Could not load {extension}",
            "color": discord.Color.red()
        }, {
            "Error Message": error_message
        }))

@client.command()
@commands.check_any(commands.is_owner(), commands.has_permissions(administrator = True))
@commands.guild_only()
async def unload(context, extension: str):
    response = await context.send(embed = create_embed({
        "title": f"Unloading {extension}...",
        "color": discord.Color.gold()
    }))

    try:
        client.unload_extension(f"cogs.{extension}")
        await response.edit(embed = create_embed({
            "title": f"Unloaded {extension}",
            "color": discord.Color.green()
        }))
    except Exception as error_message:
        await response.edit(embed = create_embed({
            "title": f"Could not unload {extension}",
            "color": discord.Color.red()
        }, {
            "Error Message": error_message
        }))

@client.command()
@commands.guild_only()
async def reload(context, extension: str):
    response = await context.send(embed = create_embed({
        "title": f"Reloading {extension}...",
        "color": discord.Color.gold()
    }))

    try:
        client.reload_extension(f"cogs.{extension}")
        await response.edit(embed = create_embed({
            "title": f"Reloaded {extension}",
            "color": discord.Color.green()
        }))
    except Exception as error_message:
        await response.edit(embed = create_embed({
            "title": f"Could not reload {extension}",
            "color": discord.Color.red()
        }, {
            "Error Message": error_message
        }))

@client.command()
@commands.guild_only()
async def update(context):
    response = await context.send(embed = create_embed({
        "title": f"Updating bot...",
        "color": discord.Color.gold()
    }))

    try:
        for extension in EXTENSIONS:
            client.reload_extension(f"cogs.{extension}")
        await response.edit(embed = create_embed({
            "title": f"Updated bot",
            "color": discord.Color.green()
        }))
    except Exception as error_message:
        await response.edit(embed = create_embed({
            "title": f"Could not update bot",
            "color": discord.Color.red()
        }, {
            "Error Message": error_message
        }))

client.remove_command("help")

for extension in EXTENSIONS:
    client.load_extension(f"cogs.{extension}")

client.run(IS_TESTING and TEST_TOKEN or TOKEN)
