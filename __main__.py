import discord
from discord.ext import commands

from secrets import TOKEN
from constants import PREFIX, EXTENSIONS

client = commands.Bot(command_prefix = PREFIX)

@client.command()
async def load(context, extension: str):
    try:
        client.load_extension(f"cogs.{extension}")
        await context.send(f"Loaded {extension}")
    except Exception as error_message:
        await context.send(error_message)

@client.command()
async def unload(context, extension: str):
    try:
        client.unload_extension(f"cogs.{extension}")
        await context.send(f"Unloaded {extension}")
    except Exception as error_message:
        await context.send(error_message)

@client.command()
async def reload(context, extension: str):
    try:
        client.reload_extension(f"cogs.{extension}")
        await context.send(f"Reloaded {extension}")
    except Exception as error_message:
        await context.send(error_message)

@client.command()
async def update(context):
    try:
        for extension in EXTENSIONS:
            client.reload_extension(f"cogs.{extension}")
        await context.send(f"Updated bot")
    except Exception as error_message:
        await context.send(error_message)

for extension in EXTENSIONS:
    client.load_extension(f"cogs.{extension}")

client.run(TOKEN)