import discord
from discord.ext import commands
import time
import asyncio
import traceback

from helper import get_guild_data, save_guild_data, get_object, create_embed, format_time, is_number, parse_to_timestamp, check_if_bot_manager, sort_dictionary, get_first_n_items, wait_for_reaction, wait_for_message
from constants import CLIENT_ID, COMMANDS, NEXT_EMOJI, BACK_EMOJI, CHANGE_EMOJI, WAIT_DELAY, ACCEPT_EMOJI, MAX_LEADERBOARD_FIELDS, THUMBS_UP, THUMBS_DOWN, DECLINE_EMOJI, COLOR_PALETTE, SUPPORTED_COLORS
from cogs.roblox import get_group_name

class change_settings():
    async def prefix(self, context, response, guild_data, value):
        value = value.lower()
        if len(value) > 1:
            await response.edit(embed = create_embed({
                'title': 'Prefix must be one letter',
                'inline': True,
                'color': discord.Color.red()
            }, guild_data))
            return
        elif is_number(value):
            await response.edit(embed = create_embed({
                'title': 'Prefix must be a letter',
                'inline': True,
                'color': discord.Coselor.red()
            }, guild_data))
            return

        new_guild_data = get_guild_data(context.guild.id)
        guild_data['prefix'], new_guild_data['prefix'] = value, value
        save_guild_data(new_guild_data)

        await response.edit(embed = create_embed({
            'title': f'Changed prefix to {value}',
            'inline': True,
            'color': discord.Color.green()
        }, guild_data))
        return guild_data, new_guild_data
    
    async def message_cooldown(self, context, response, guild_data, value):
        seconds = parse_to_timestamp(value)
        if not seconds:
            await response.edit(embed = create_embed({
                'title': 'Could not parse {value}',
                'inline': True,
                'color': discord.Color.red(),
            }, guild_data))
            return

        new_guild_data = get_guild_data(context.guild.id)
        guild_data['message_cooldown'], new_guild_data['message_cooldown'] = seconds, seconds
        save_guild_data(new_guild_data)

        await response.edit(embed = create_embed({
            'title': f'Changed message cooldown to {value} ({seconds} seconds)',
            'inline': True,
            'color': discord.Color.green()
        }, guild_data))
        return guild_data, new_guild_data
    
    async def daily_reward(self, context, response, guild_data, value):
        if not is_number(value):
            await response.edit(embed = create_embed({
                'title': f'The daily reward ({value}) must be a number',
                'color': discord.Color.red(),
                'inline': True,
            }, guild_data))
            return
        
        value = int(value)
        if value < 0:
            await response.edit(embed = create_embed({
                'title': f'The daily reward ({value}) must be greater than or equal to 0',
                'color': discord.Color.red(),
                'inline': True,
            }, guild_data))
            return

        new_guild_data = get_guild_data(context.guild.id)
        guild_data['daily_reward'], new_guild_data['daily_reward'] = value, value
        save_guild_data(new_guild_data)

        await response.edit(embed = create_embed({
            'title': f'Changed daily reward to {value}',
            'inline': True,
            'color': discord.Color.green()
        }, guild_data))
        return guild_data, new_guild_data
    
    async def point_channels(self, context, response, guild_data, value):
        channel = get_object(context.guild.text_channels, value)
        if not channel:
            await response.edit(embed = create_embed({
                'title': f'Could not find text channel {channel or value}',
                'color': discord.Color.red(),
                'inline': True,
            }, guild_data))
            return

        new_guild_data = get_guild_data(context.guild.id)
        if channel.id in new_guild_data['point_channels']:
            new_guild_data['point_channels'].remove(channel.id)
            save_guild_data(new_guild_data)

            if len(new_guild_data['point_channels']) > 0:
                point_channels = []
                for point_channel_id in new_guild_data['point_channels']:
                    point_channel = context.guild.get_channel(point_channel_id)
                    if point_channel:
                        point_channels.append(point_channel.mention)
                guild_data['point_channels'] = ', '.join(point_channels)
            else:
                guild_data['point_channels'] = 'None'

            await response.edit(embed = create_embed({
                'title': f'Removed text channel {channel} from point channels',
                'color': discord.Color.green(),
                'inline': True,
            }, guild_data))
            return guild_data, new_guild_data
        else:
            new_guild_data['point_channels'].append(channel.id)
            guild_data['point_channels'] += f', {channel.mention}'
            save_guild_data(new_guild_data)

            if new_guild_data.get('point_channels') and len(new_guild_data['point_channels']) > 0:
                point_channels = []
                for point_channel_id in new_guild_data['point_channels']:
                    point_channel = context.guild.get_channel(point_channel_id)
                    if point_channel:
                        point_channels.append(point_channel.mention)
                guild_data['point_channels'] = ', '.join(point_channels)
            else:
                guild_data['point_channels'] = 'None'

            await response.edit(embed = create_embed({
                'title': f'Added text channel {channel} to point channels',
                'color': discord.Color.green(),
                'inline': True,
            }, guild_data))
            return guild_data, new_guild_data
    
    async def points_per_message(self, context, response, guild_data, value):
        if not is_number(value):
            await response.edit(embed = create_embed({
                'title': f'The points per message ({value}) must be a number',
                'color': discord.Color.red(),
                'inline': True,
            }, guild_data))
            return
        
        value = int(value)
        if value < 0:
            await response.edit(embed = create_embed({
                'title': f'The points per message ({value}) must be greater than or equal to 0',
                'color': discord.Color.red(),
                'inline': True,
            }, guild_data))
            return

        new_guild_data = get_guild_data(context.guild.id)
        guild_data['points_per_message'], new_guild_data['points_per_message'] = value, value
        save_guild_data(new_guild_data)

        await response.edit(embed = create_embed({
            'title': f'Changed points per message to {value}',
            'inline': True,
            'color': discord.Color.green()
        }, guild_data))
        return guild_data, new_guild_data
    
    async def qotd_channel(self, context, response, guild_data, value):
        if value.lower() == 'none':
            new_guild_data = get_guild_data(context.guild.id)
            new_guild_data['qotd_channel'], guild_data['qotd_channel'] = None, None
            save_guild_data(new_guild_data)
            
            await response.edit(embed = create_embed({
                'title': f'Removed QOTD channel',
                'color': discord.Color.green(),
                'inline': True,
            }, guild_data))
            return guild_data, new_guild_data
        else:
            channel = get_object(context.guild.text_channels, value)
            if not channel:
                await response.edit(embed = create_embed({
                    'title': f'Could not find text channel {channel or value}',
                    'color': discord.Color.red(),
                    'inline': True,
                }, guild_data))
                return

            new_guild_data = get_guild_data(context.guild.id)
            new_guild_data['qotd_channel'] = channel.id
            guild_data['qotd_channel'] = channel.mention
            save_guild_data(new_guild_data)

            await response.edit(embed = create_embed({
                'title': f'Changed QOTD channel to {channel}',
                'color': discord.Color.green(),
                'inline': True,
            }, guild_data))
            return guild_data, new_guild_data
    
    async def aotd_keywords(self, context, response, guild_data, value):
        new_guild_data = get_guild_data(context.guild.id)
        value = value.lower()
        if value in new_guild_data['aotd_keywords']:
            new_guild_data['aotd_keywords'].remove(value)
            guild_data['aotd_keywords'] = len(new_guild_data['aotd_keywords']) > 0 and ', '.join(new_guild_data['aotd_keywords']) or 'None'
            save_guild_data(new_guild_data)

            await response.edit(embed = create_embed({
                'title': f'Removed {value} as an AOTD keywords',
                'color': discord.Color.green(),
                'inline': True,
            }, guild_data))
            return guild_data, new_guild_data
        else:
            new_guild_data['aotd_keywords'].append(value)
            guild_data['aotd_keywords'] = len(new_guild_data['aotd_keywords']) > 0 and ', '.join(new_guild_data['aotd_keywords']) or 'None'
            save_guild_data(new_guild_data)

            await response.edit(embed = create_embed({
                'title': f'Added {value} as an AOTD keywords',
                'color': discord.Color.green(),
                'inline': True,
            }, guild_data))
            return guild_data, new_guild_data
    
    async def points_per_aotd(self, context, response, guild_data, value):
        if not is_number(value):
            await response.edit(embed = create_embed({
                'title': f'The points per AOTD ({value}) must be a number',
                'color': discord.Color.red(),
                'inline': True,
            }, guild_data))
            return
        
        value = int(value)
        if value < 0:
            await response.edit(embed = create_embed({
                'title': f'The points per AOTD ({value}) must be greater than or equal to 0',
                'color': discord.Color.red(),
                'inline': True,
            }, guild_data))
            return

        new_guild_data = get_guild_data(context.guild.id)
        guild_data['points_per_aotd'], new_guild_data['points_per_aotd'] = value, value
        save_guild_data(new_guild_data)

        await response.edit(embed = create_embed({
            'title': f'Changed points per AOTD to {value}',
            'inline': True,
            'color': discord.Color.green()
        }, guild_data))
        return guild_data, new_guild_data
    
    async def giveaway_channel(self, context, response, guild_data, value):
        if value.lower() == 'none':
            new_guild_data = get_guild_data(context.guild.id)
            new_guild_data['giveaway_channel'], guild_data['giveaway_channel'] = None, None
            save_guild_data(new_guild_data)

            await response.edit(embed = create_embed({
                'title': f'Removed giveaway channel',
                'color': discord.Color.green(),
                'inline': True,
            }, guild_data))
            return guild_data, new_guild_data
        else:
            channel = get_object(context.guild.text_channels, value)
            if not channel:
                await response.edit(embed = create_embed({
                    'title': f'Could not find text channel {channel or value}',
                    'color': discord.Color.red(),
                    'inline': True,
                }, guild_data))
                return

            new_guild_data = get_guild_data(context.guild.id)
            new_guild_data['giveaway_channel'] = channel.id
            guild_data['giveaway_channel'] = channel.mention
            save_guild_data(new_guild_data)

            await response.edit(embed = create_embed({
                'title': f'Changed giveaway channel to {channel}',
                'color': discord.Color.green(),
                'inline': True,
            }, guild_data))
            return guild_data, new_guild_data
    
    async def suggestion_channel(self, context, response, guild_data, value):
        if value.lower() == 'none':
            new_guild_data = get_guild_data(context.guild.id)
            new_guild_data['suggestion_channel'], guild_data['suggestion_channel'] = None, None
            save_guild_data(new_guild_data)

            await response.edit(embed = create_embed({
                'title': f'Removed suggestion channel',
                'color': discord.Color.green(),
                'inline': True,
            }, guild_data))
            return guild_data, new_guild_data
        else:
            channel = get_object(context.guild.text_channels, value)
            if not channel:
                await response.edit(embed = create_embed({
                    'title': f'Could not find text channel {channel or value}',
                    'color': discord.Color.red(),
                    'inline': True,
                }, guild_data))
                return

            new_guild_data = get_guild_data(context.guild.id)
            new_guild_data['suggestion_channel'] = channel.id
            guild_data['suggestion_channel'] = channel.mention
            save_guild_data(new_guild_data)

            await response.edit(embed = create_embed({
                'title': f'Changed suggestion channel to {channel}',
                'color': discord.Color.green(),
                'inline': True,
            }, guild_data))
            return guild_data, new_guild_data

    async def roblox_groups(self, context, response, guild_data, value):
        if not is_number(value):
            await response.edit(embed = create_embed({
                'title': f'The roblox group ID {value} must be a number',
                'color': discord.Color.red(),
                'inline': True,
            }, guild_data))
            return

        group_name = await get_group_name(value)
        if not group_name:
            await response.edit(embed = create_embed({
                'title': f'Could not find roblox group with ID {value}',
                'color': discord.Color.red(),
                'inline': True,
            }, guild_data))
            return

        new_guild_data = get_guild_data(context.guild.id)
        if value in new_guild_data['roblox_groups']:
            new_guild_data['roblox_groups'].remove(value)
            save_guild_data(new_guild_data)

            if new_guild_data.get('roblox_groups') and len(new_guild_data['roblox_groups']) > 0:
                roblox_groups = []
                for group_id in new_guild_data['roblox_groups']:
                    group_name = await get_group_name(group_id)
                    if group_name:
                        roblox_groups.append(f'{group_name} ({group_id})')
                guild_data['roblox_groups'] = ', '.join(roblox_groups)
            else:
                guild_data['roblox_groups'] = 'None'

            await response.edit(embed = create_embed({
                'title': f'Removed {group_name} ({value}) as a roblox group',
                'color': discord.Color.green(),
                'inline': True,
            }, guild_data))
            return guild_data, new_guild_data
        else:
            new_guild_data['roblox_groups'].append(value)
            save_guild_data(new_guild_data)

            if new_guild_data.get('roblox_groups') and len(new_guild_data['roblox_groups']) > 0:
                roblox_groups = []
                for group_id in new_guild_data['roblox_groups']:
                    group_name = await get_group_name(group_id)
                    if group_name:
                        roblox_groups.append(f'{group_name} ({group_id})')
                guild_data['roblox_groups'] = ', '.join(roblox_groups)
            else:
                guild_data['roblox_groups'] = 'None'

            await response.edit(embed = create_embed({
                'title': f'Added {group_name} ({value}) as a roblox group',
                'color': discord.Color.green(),
                'inline': True,
            }, guild_data))
            return guild_data, new_guild_data
    
    async def roblox_games(self, context, response, guild_data, value):
        if not is_number(value):
            await response.edit(embed = create_embed({
                'title': f'The roblox game ID {value} must be a number',
                'color': discord.Color.red(),
                'inline': True,
            }, guild_data))
            return

        new_guild_data = get_guild_data(context.guild.id)
        if value in new_guild_data['roblox_games']:
            new_guild_data['roblox_games'].remove(value)
            save_guild_data(new_guild_data)

            if new_guild_data.get('roblox_games') and len(new_guild_data['roblox_games']) > 0:
                guild_data['roblox_games'] = ', '.join(str(game_id) for game_id in new_guild_data['roblox_games'])
            else:
                guild_data['roblox_games'] = 'None'

            await response.edit(embed = create_embed({
                'title': f'Removed game with id {value} as a roblox game',
                'color': discord.Color.green(),
                'inline': True,
            }, guild_data))
            return guild_data, new_guild_data
        else:
            new_guild_data['roblox_games'].append(value)
            save_guild_data(new_guild_data)

            if new_guild_data.get('roblox_games') and len(new_guild_data['roblox_games']) > 0:
                guild_data['roblox_games'] = ', '.join(str(game_id) for game_id in new_guild_data['roblox_games'])
            else:
                guild_data['roblox_games'] = 'None'

            await response.edit(embed = create_embed({
                'title': f'Added game with id {value} as a roblox game',
                'color': discord.Color.green(),
                'inline': True,
            }, guild_data))
            return guild_data, new_guild_data
    
    async def group_award(self, context, response, guild_data, value):
        if not is_number(value):
            await response.edit(embed = create_embed({
                'title': f'The group award ({value}) must be a number',
                'color': discord.Color.red(),
                'inline': True,
            }, guild_data))
            return

        value = int(value)
        if value < 0:
            await response.edit(embed = create_embed({
                'title': f'The group award ({value}) must be greater than or equal to 0',
                'color': discord.Color.red(),
                'inline': True,
            }, guild_data))
            return

        new_guild_data = get_guild_data(context.guild.id)
        new_guild_data['group_award'], guild_data['group_award'] = value, value
        save_guild_data(new_guild_data)

        await response.edit(embed = create_embed({
            'title': f'Changed group award to {value}',
            'inline': True,
            'color': discord.Color.green()
        }, guild_data))
        return guild_data, new_guild_data
    
    async def game_award(self, context, response, guild_data, value):
        if not is_number(value):
            await response.edit(embed = create_embed({
                'title': f'The game award ({value}) must be a number',
                'color': discord.Color.red(),
                'inline': True,
            }, guild_data))
            return

        value = int(value)
        if value < 0:
            await response.edit(embed = create_embed({
                'title': f'The game award ({value}) must be greater than or equal to 0',
                'color': discord.Color.red(),
                'inline': True,
            }, guild_data))
            return

        new_guild_data = get_guild_data(context.guild.id)
        guild_data['game_award'], new_guild_data['game_award'] = value, value
        save_guild_data(new_guild_data)

        await response.edit(embed = create_embed({
            'title': f'Changed game award to {value}',
            'inline': True,
            'color': discord.Color.green()
        }, guild_data))
        return guild_data, new_guild_data
    
    async def bot_manager(self, context, response, guild_data, value):
        if value.lower() == 'none':
            new_guild_data = get_guild_data(context.guild.id)
            guild_data['bot_manager'], new_guild_data['bot_manager'] = None, None
            save_guild_data(new_guild_data)

            await response.edit(embed = create_embed({
                'title': f'Removed bot manager role',
                'inline': True,
                'color': discord.Color.green()
            }, guild_data))
            return guild_data, new_guild_data
        else:
            role = get_object(context.guild.roles, value)
            if not role:
                await response.edit(embed = create_embed({
                    'title': f'Could not find role {role}',
                    'color': discord.Color.red(),
                    'inline': True,
                }, guild_data))
                return

            new_guild_data = get_guild_data(context.guild.id)
            new_guild_data['bot_manager'] = role.id
            guild_data['bot_manager'] = role.mention
            save_guild_data(new_guild_data)

            await response.edit(embed = create_embed({
                'title': f'Changed bot manager role to {role}',
                'inline': True,
                'color': discord.Color.green()
            }, guild_data))
            return guild_data, new_guild_data
    
    async def giveaway_manager(self, context, response, guild_data, value):
        if value.lower() == 'none':
            new_guild_data = get_guild_data(response.id)
            guild_data['giveaway_manager'], new_guild_data['giveaway_manager'] = None, None
            save_guild_data(new_guild_data)

            await response.edit(embed = create_embed({
                'title': f'Removed giveaway manager role',
                'inline': True,
                'color': discord.Color.green()
            }, guild_data))
            return guild_data, new_guild_data
        else:
            role = get_object(context.guild.roles, value)
            if not role:
                await response.edit(embed = create_embed({
                    'title': f'Could not find role {value}',
                    'color': discord.Color.red(),
                    'inline': True,
                }, guild_data))
                return

            new_guild_data = get_guild_data(context.guild.id)
            new_guild_data['giveaway_manager'] = role.id
            guild_data['giveaway_manager'] = role.mention
            save_guild_data(new_guild_data)

            await response.edit(embed = create_embed({
                'title': f'Changed bot manager role to {role}',
                'inline': True,
                'color': discord.Color.green()
            }, guild_data))
            return guild_data, new_guild_data

class default(commands.Cog):
    def __init__(self, client):
        self.client = client
        self.uptime = time.time()
 
    @commands.command()
    async def info(self, context):
        response = await context.send(embed = create_embed({
            'title': f'Loading bot info...',
            'color': discord.Color.gold()
        }))

        try:
            ping = round(self.client.latency * 1000)
            invite_url = discord.utils.oauth_url(client_id = CLIENT_ID, permissions = discord.Permissions(8))
            uptime = format_time(round(time.time() - self.uptime))
            servers = len(await self.client.fetch_guilds(limit = None).flatten())
            users = len([member for member in self.client.get_all_members()])

            await response.edit(embed = create_embed({
                'title': f'Invite',
                'url': invite_url,
            }, {
                'Ping': f'{ping} ms',
                'Uptime': uptime,
                'Servers': servers,
                'Users': users
            }))
        except Exception as error_message:
            await response.edit(embed = create_embed({
                'title': f'Could not load bot info',
                'color': discord.Color.red()
            }, {
                'Error Message': error_message
            }))
 
    @commands.command()
    async def help(self, context):
        response = await context.send(embed = create_embed({
            'title': f'Loading commands...',
            'color': discord.Color.gold()
        }))

        try:
            pages = []
            current_page = 0
            for category, commands in COMMANDS.items():
                pages.append(create_embed({
                    'title': category,
                }, commands))

            await response.edit(embed = pages[current_page])

            while True:
                try:
                    await response.add_reaction(BACK_EMOJI)
                    await response.add_reaction(NEXT_EMOJI)

                    reaction, user = await wait_for_reaction(self.client, context, [BACK_EMOJI, NEXT_EMOJI], timeout=60)
                    if not reaction:
                        return
                    elif str(reaction.emoji) == NEXT_EMOJI:
                        if current_page + 1 >= len(pages):
                            current_page = len(pages) - 1
                        else:
                            current_page += 1
                    elif str(reaction.emoji) == BACK_EMOJI:
                        if current_page == 0:
                            current_page = 0
                        else:
                            current_page -= 1

                    if context.guild:
                        await response.edit(embed = pages[current_page])
                        await response.remove_reaction(reaction.emoji, user)
                    else:
                        response = await context.send(embed = pages[current_page])
                except asyncio.TimeoutError:
                    await response.edit(embed = pages[current_page])
                    await response.clear_reactions()
                    return
        except Exception as error_message:
            await response.edit(embed = create_embed({
                'title': f'Could not load commands',
                'color': discord.Color.red()
            }, {
                'Error Message': error_message
            }))

    @commands.command()
    @commands.check_any(commands.is_owner(), commands.check(check_if_bot_manager))
    @commands.guild_only()
    async def settings(self, context):
        response = await context.send(embed = create_embed({
            'title': f'Loading settings...',
            'color': discord.Color.gold()
        }))
        
        try:
            while True:
                # format settings
                guild_data = get_guild_data(context.guild.id)
                for key, value in guild_data.copy().items():
                    if key in ['_id', 'guild_id']:
                        guild_data.pop(key)
                    elif key in ['aotd_keywords', 'roblox_games']:
                        guild_data[key] = len(value) > 0 and ', '.join(value) or 'None'
                    elif key in ['qotd_channel', 'giveaway_channel', 'suggestion_channel']:
                        channel = context.guild.get_channel(value or 0)
                        if channel:
                            guild_data[key] = channel.mention
                    elif key in ['point_channels']:
                        if len(value) > 0:
                            channels = []
                            for channel_id in guild_data[key]:
                                channel = context.guild.get_channel(channel_id)
                                if channel:
                                    channels.append(channel.mention)
                            guild_data[key] = ', '.join(channels)
                        else:
                            guild_data[key] = 'None'
                    elif key in ['bot_manager', 'giveaway_manager']:
                        role = context.guild.get_role(value or 0)
                        if role:
                            guild_data[key] = role.mention
                    elif key in ['roblox_groups']:
                        if len(value) > 0:
                            roblox_groups = []
                            for group_id in value:
                                group_name = await get_group_name(group_id)
                                if group_name:
                                    roblox_groups.append(f'{group_name} ({group_id})')
                            guild_data['roblox_groups'] = ', '.join(roblox_groups)
                        else:
                            guild_data['roblox_groups'] = 'None'

                # get input
                await response.edit(embed = create_embed({
                    'title': f'Guild Settings',
                    'description': f'Press the {CHANGE_EMOJI} to change settings',
                    'inline': True,
                }, guild_data))

                await response.add_reaction(CHANGE_EMOJI)
                reaction, user = await wait_for_reaction(self.client, context, CHANGE_EMOJI, 30)
                if not reaction:
                    await response.edit(embed = create_embed({
                        'title': f'Guild Settings',
                        'inline': True,
                    }, guild_data))
                    await response.clear_reaction(CHANGE_EMOJI)
                    return
                    
                # get setting
                await response.clear_reaction(CHANGE_EMOJI)
                await response.edit(embed = create_embed({
                    'title': 'Please type the setting you would like to change',
                    'inline': True,
                    'color': discord.Color.gold()
                }, guild_data))

                message = await wait_for_message(self.client, context, 30)
                if not message:
                    await response.edit(embed = create_embed({
                        'title': f'You did not enter a setting to change',
                        'inline': True,
                        'color': discord.Color.red()
                    }, guild_data))
                    await asyncio.sleep(WAIT_DELAY)
                    continue

                await message.delete()
                name = message.content.lower()
                if not name in guild_data.keys():
                    await response.edit(embed = create_embed({
                        'title': f'{name} is an invalid setting',
                        'inline': True,
                        'color': discord.Color.red()
                    }, guild_data))
                    await asyncio.sleep(WAIT_DELAY)
                    continue

                # get value
                await response.edit(embed = create_embed({
                    'title': f'Please type the value you would like to change {name} to',
                    'inline': True,
                    'color': discord.Color.gold()
                }, guild_data))

                message = await wait_for_message(self.client, context, 30)
                if not message:
                    await response.edit(embed = create_embed({
                        'title': f'You did not enter a setting to change',
                        'inline': True,
                        'color': discord.Color.red()
                    }, guild_data))
                    await asyncio.sleep(WAIT_DELAY)
                    continue

                value = message.content
                await message.delete()

                # change settings
                if name in dir(change_settings):
                    new_guild_data = await getattr(change_settings(), name)(context, response, guild_data, value)
                    if new_guild_data:
                        guild_data = new_guild_data
                    await asyncio.sleep(WAIT_DELAY)
                else:
                    await response.edit(embed = create_embed({
                        'title': f'{name} is an invalid setting',
                        'color': discord.Color.red()
                    }))
                    await asyncio.sleep(WAIT_DELAY)
        except Exception as error_message:
            traceback.print_exc()
            await response.edit(embed = create_embed({
                'title': f'Could not load settings',
                'color': discord.Color.red()
            }, {
                'Error Message': error_message
            }))

    @commands.command()
    async def messageleaderboard(self, context):
        response = await context.send(embed = create_embed({
            'title': 'Loading message leaderboard...',
            'description': f'React with {ACCEPT_EMOJI} to be pinged when the message leaderboard is done. This process could hours at most depending on the amount of messages in a server.',
            'color': discord.Color.gold()
        }))

        await response.add_reaction(ACCEPT_EMOJI)

        try:
            members = {}
            async def get_messages_in_guild(guild):
                for channel in guild.text_channels:
                    messages = await channel.history(limit = None).flatten()
                    for message in messages:
                        author = message.author
                        if not guild.get_member(author.id):
                            continue

                        if not members.get(author.name):
                            members[author.name] = 1
                        else:
                            members[author.name] += 1

            if context.guild:
                await get_messages_in_guild(context.guild)
            else:
                for guild in self.client.guilds:
                    await get_messages_in_guild(guild)

            await response.edit(embed = create_embed({
                'title': f'Loading message leaderboard (sorting leaderboard)...',
                'description': f'React with {ACCEPT_EMOJI} to be pinged when the message leaderboard is done',
                'color': discord.Color.gold()
            }))

            members = sort_dictionary(members, True)
            members = get_first_n_items(members, MAX_LEADERBOARD_FIELDS)

            await response.edit(embed = create_embed({
                'title': context.guild and 'Message Leaderboard (Current Server)' or 'Message Leaderboard (All Servers)'
            }, members))

            response2 = await response.channel.fetch_message(response.id)
            for reaction in response2.reactions:
                if str(reaction.emoji) == ACCEPT_EMOJI:
                    users = [] 
                    async for user in reaction.users():
                        if not user.bot:
                            users.append(user.mention)

                    if len(users) > 0:
                        ping = ' '.join(users)
                        await context.send(' '.join(users))
                    break

        except Exception as error_message:
            await response.edit(embed = create_embed({
                'title': 'Could not load message leaderboard',
                'color': discord.Color.red()
            }, {
                'Error Message': error_message
            }))

    @commands.command()
    @commands.guild_only()
    async def suggest(self, context):
        response = await context.send(embed=create_embed({
            'title': 'Creating suggestion...',
            'color': discord.Color.gold()
        }))

        try:
            guild_data = get_guild_data(context.guild.id)

            suggestion_channel_id = guild_data.get('suggestion_channel')
            if not suggestion_channel_id:
                await response.edit(embed=create_embed({
                    'title': 'Server does not have a suggestion channel',
                    'color': discord.Color.red(),
                }))
                return

            suggestion_channel = context.guild.get_channel(suggestion_channel_id)
            if not suggestion_channel:
                await response.edit(embed=create_embed({
                    'title': 'Server does not have a suggestion channel',
                    'color': discord.Color.red(),
                }))
                return

            await response.edit(embed=create_embed({
                'title': 'Enter a title for the suggestion',
                'color': discord.Color.gold()
            }))

            message = await wait_for_message(self.client, context, timeout=120)
            if not message:
                await response.edit(embed=create_embed({
                    'title': 'No response',
                    'color': discord.Color.red(),
                }))
                return

            title = message.content
            await message.delete()
            await response.edit(embed=create_embed({
                'title': 'Enter a description for the suggestion',
                'color': discord.Color.gold()
            }))

            message = await wait_for_message(self.client, context, timeout=300)
            if not message:
                await response.edit(embed=create_embed({
                    'title': 'No response',
                    'color': discord.Color.red(),
                }))
                return

            description = message.content
            await message.delete()
            suggestion_message = await suggestion_channel.send(embed=create_embed({
                'title': title,
                'description': description,
                'author': context.author,
            }))
            await suggestion_message.add_reaction(THUMBS_UP)
            await suggestion_message.add_reaction(THUMBS_DOWN)

            await response.edit(embed=create_embed({
                'title': 'Created Suggestion',
                'color': discord.Color.green(),
                'url': suggestion_message.jump_url,
            }, {
                'title': title,
                'description': description,
            }))

        except Exception as error_message:
            import traceback
            traceback.print_exc()

            await response.edit(embed=create_embed({
                'title': 'Could not create suggestion',
                'color': discord.Color.red(),
            }, {
                'Error Message': error_message,
            }))

            print('Could not create suggestion')
            print(error_message)

    @commands.command()
    @commands.guild_only()
    async def embed(self, context):
        response = await context.send(embed=create_embed({
            'title': 'Creating embed...',
            'color': discord.Color.gold()
        }))

        async def get_text(title=None, description=None, url=None):
            await response.edit(embed=create_embed({
                'title': title,
                'description': description or 'Type "skip" to skip. Type "cancel" to stop the process.',
                'url': url,
                'color': discord.Color.gold()
            }))

            message = await wait_for_message(self.client, context, timeout=120)
            if not message:
                await response.edit(embed=create_embed({
                    'title': 'No response',
                    'color': discord.Color.red(),
                }))
                return 'cancel'

            content = message.content
            await message.delete()
            if content == 'cancel':
                await response.edit(embed=create_embed({
                    'title': 'Process canceled',
                    'color': discord.Color.red(),
                }))
                return 'cancel'
            else:
                return content

        async def get_file(title=None, description=None):
            await response.edit(embed=create_embed({
                'title': title,
                'description': description or 'Type "skip" to skip. Type "cancel" to stop the process.',
                'color': discord.Color.gold()
            }))

            message = await wait_for_message(self.client, context, timeout=120)
            if not message:
                await response.edit(embed=create_embed({
                    'title': 'No response',
                    'color': discord.Color.red(),
                }))
                return

            content = message.content
            attachments = message.attachments
            await message.delete()

            if content == 'cancel':
                await response.edit(embed=create_embed({
                    'title': 'Process canceled',
                    'color': discord.Color.red(),
                }))
                return 'cancel'
            elif content == 'skip':
                return 'skip'
            elif attachments and len(attachments) > 0:
                return attachments[0].url

        try:
            properties = {}
            fields = {}

            # title
            title = await get_text('Enter the title of the embed')
            if title == 'cancel':
                return
            elif len(title) >= 256:
                await response.edit(embed=create_embed({
                    'title': 'Title is longer than 256 characters',
                    'color': discord.Color.red()
                }))
                return
            elif title != 'skip':
                properties['title'] = title

            # description
            description = await get_text('Enter the description of the embed')
            if description == 'cancel':
                return
            elif description == 'skip':
                if not properties.get('title'):
                    await response.edit(embed=create_embed({
                        'title': 'Since there is no title, a description is required',
                        'color': discord.Color.red()
                    }))
                    return
            elif len(description) >= 4096:
                await response.edit(embed=create_embed({
                    'title': 'Description is longer than 4096 characters',
                    'color': discord.Color.red()
                }))
                return
            else:
                properties['description'] = description

            # color
            color = await get_text('Enter the color of the embed', 'View supported colors by pressing the link above. Type "skip" to use the default color. Type "cancel" to stop the process.', COLOR_PALETTE)
            if color == 'cancel':
                return
            elif color == 'skip':
                color = discord.Color.default()
            elif not SUPPORTED_COLORS.get(color):
                await response.edit(embed=create_embed({
                    'title': f'{color} is not a supported color',
                    'description': 'View supported colors by pressing the link above',
                    'url': COLOR_PALETTE,
                    'color': discord.Color.red()
                }))
                return
            else:
                properties['color'] = SUPPORTED_COLORS.get(color)

            # url
            if properties['title'] != '':
                url = await get_text('Enter the url of the embed')
                if url == 'cancel':
                    return
                elif url != 'skip':
                    if not url.startswith('http'):
                        await response.edit(embed=create_embed({
                            'title': f'{url} is is an invalud url',
                            'color': discord.Color.red()
                        }))
                        return
                    else:
                        properties['url'] = url

            # author
            author = await get_text('Enter the author of the embed')
            if author == 'cancel':
                return
            elif author != 'skip':
                user = get_object(context.guild.members, author)
                if not user:
                    await response.edit(embed=create_embed({
                        'title': f'Could not find member {author}',
                        'color': discord.Color.red(),
                    }))
                    return
                else:
                    properties['author'] = user

            # footer
            footer = await get_text('Enter the footer of the embed')
            if footer == 'cancel':
                return
            elif len(footer) >= 2048:
                await response.edit(embed=create_embed({
                    'title': 'Footer is longer than 2048 characters',
                    'color': discord.Color.red()
                }))
                return
            elif title != 'skip':
                properties['footer'] = footer

            # image
            image = await get_file('Enter the image of the embed.')
            if image == 'cancel':
                return
            elif not image:
                await response.edit(embed=create_embed({
                    'title': f'Invalid Image',
                    'color': discord.Color.red(),
                }))
                return
            elif image == 'skip':
                pass
            elif not image.endswith('.png'):
                await response.edit(embed=create_embed({
                    'title': f'Invalid Image Format',
                    'color': discord.Color.red(),
                }))
                return
            else:
                properties['image'] = image

            # thumbnail
            thumbnail = await get_file('Enter the thumbnail of the embed.')
            if thumbnail == 'cancel':
                return
            elif not thumbnail:
                await response.edit(embed=create_embed({
                    'title': f'Invalid Image',
                    'color': discord.Color.red(),
                }))
                return
            elif thumbnail == 'skip':
                pass
            elif not thumbnail.endswith('.png'):
                await response.edit(embed=create_embed({
                    'title': f'Invalid Image Format',
                    'color': discord.Color.red(),
                }))
                return
            else:
                properties['thumbnail'] = thumbnail

            # fields
            while True:
                field_name = await get_text('Enter the name of a field')
                if field_name == 'cancel':
                    return
                elif field_name == 'skip':
                    break
                elif len(field_name) >= 256:
                    await response.edit(embed=create_embed({
                        'title': 'Name is longer than 256 characters',
                        'color': discord.Color.red()
                    }))
                    return
                else:
                    field_value = await get_text('Enter the value of a field', 'Type "cancel" to stop the process.')
                    if field_value == 'cancel':
                        return
                    elif len(field_value) >= 1024:
                            await response.edit(embed=create_embed({
                                'title': 'Value is longer than 1024 characters',
                                'color': discord.Color.red()
                            }))
                            return
                    else:
                        fields[field_name] = field_value

            # channel
            channel = await get_text('Enter the channel you want to send the embed to.', 'Type "skip" to send in this channel. Type "cancel" to stop the process.')
            if channel == 'cancel':
                return
            elif channel == 'skip':
                channel = context.channel
            elif channel != 'skip':
                located_channel = get_object(context.guild.text_channels, channel)
                if located_channel:
                    channel = located_channel
                else:
                    await response.edit(embed=create_embed({
                        'title': f'Could not find channel {channel}',
                        'color': discord.Color.red(),
                    }))
                    return

            # preview & send
            preview = await context.send(embed=create_embed(properties, fields))

            await response.add_reaction(ACCEPT_EMOJI)
            await response.add_reaction(DECLINE_EMOJI)
            await response.edit(embed=create_embed({
                'title': f'This is a preview of the embed. React with {ACCEPT_EMOJI} to send the embed in #{channel.name} or {DECLINE_EMOJI} to cancel'
            }))

            reaction, user = await wait_for_reaction(self.client, context, emoji=[ACCEPT_EMOJI, DECLINE_EMOJI], timeout=60)
            await response.clear_reactions()
            await preview.delete()
            if not reaction:
                await response.edit(embed=create_embed({
                    'title': 'No response',
                    'color': discord.Color.red(),
                }))
                return
            elif reaction.emoji == DECLINE_EMOJI:
                await response.edit(embed=create_embed({
                    'title': 'Process canceled',
                    'color': discord.Color.red(),
                }))
                return

            await channel.send(embed=create_embed(properties, fields))
            await response.edit(embed=create_embed({
                'title': f'Embed sent in #{channel.name}',
                'color': discord.Color.green()
            }))
        except Exception as error_message:
            await response.edit(embed=create_embed({
                'title': 'Could not create embed',
                'color': discord.Color.red()
            }, {
                'Error Message': error_message
            }))

def setup(client):
    client.add_cog(default(client))
