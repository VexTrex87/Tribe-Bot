import discord
from discord.ext import commands
import time
import math
from helper import get_user_data, save_user_data, get_all_user_data, get_guild_data, create_embed, check_if_bot_manager, sort_dictionary, wait_for_reaction, get_all_user_data
from constants import MAX_LEADERBOARD_FIELDS, ACCEPT_EMOJI

class points(commands.Cog):
    def __init__(self, client):
        self.client = client

    @commands.command()
    async def points(self, context, member: discord.Member = None):
        if not member:
            member = context.author

        response = await context.send(embed = create_embed({
            'title': f'Loading points for {member}...',
            'color': discord.Color.gold()
        }))
        
        try:
            user_data = get_user_data(member.id)
            points = user_data['points']
            await response.edit(embed = create_embed({
                'title': f'{points} points',
            }))
        except Exception as error_message:
            await response.edit(embed = create_embed({
                'title': f'Could not load {member}\'s points',
                'color': discord.Color.red()
            }, {
                'Error Message': error_message
            }))
            
    @commands.command()
    @commands.check(check_if_bot_manager)
    @commands.guild_only()
    async def setpoints(self, context, member: discord.Member, amount: int):
        response = await context.send(embed = create_embed({
            'title': f'Changing {member}\'s points to {amount}...',
            'color': discord.Color.gold()
        }))
        
        try:
            if amount < 0:
                await response.edit(embed = create_embed({
                    'title': f'The amount of points ({amount}) cannot be less than 0',
                    'color': discord.Color.red()
                }))
                return

            user_data = get_user_data(member.id) 
            user_data['points'] = amount
            save_user_data(user_data)

            await response.edit(embed = create_embed({
                'title': f'Set {member}\'s points to {amount}',
                'color': discord.Color.green()
            }))

            try:
                await member.send(embed = create_embed({
                    'title': f'{context.author} set your points to {amount}',
                }))
            except discord.Forbidden:
                print('Cannot DM {} to tell them that {} changed their points to {}'.format(member, context.author, amount))
        except Exception as error_message:
            await response.edit(embed = create_embed({
                'title': f'Could not set {member}\'s points to {amount}',
                'color': discord.Color.red()
            }, {
                'Error Message': error_message
            }))
            
    @commands.command()
    @commands.check(check_if_bot_manager)
    @commands.guild_only()
    async def addpoints(self, context, member: discord.Member, amount: int):
        response = await context.send(embed = create_embed({
            'title': f'Adding {amount} points to {member}...',
            'color': discord.Color.gold()
        }))
        
        try:
            if amount < 0:
                await response.edit(embed = create_embed({
                    'title': f'The amount of points ({amount}) cannot be less than 0',
                    'color': discord.Color.red()
                }))
                return

            user_data = get_user_data(member.id)
            user_data['points'] += amount
            save_user_data(user_data)
            
            await response.edit(embed = create_embed({
                'title': f'Gave {amount} points to {member}',
                'color': discord.Color.green()
            }))

            try:
                await member.send(embed = create_embed({
                    'title': f'{context.author} gave you {amount} points',
                }))
            except discord.Forbidden:
                print('Cannot tell {} that {} gave them {} points'.format(member, context.author, amount))
        except Exception as error_message:
            await response.edit(embed = create_embed({
                'title': f'Could not give {amount} points to {member}',
                'color': discord.Color.red()
            }, {
                'Error Message': error_message
            }))
            
    @commands.command()
    @commands.guild_only()
    async def daily(self, context):
        response = await context.send(embed = create_embed({
            'title': f'Giving daily trestf...',
            'color': discord.Color.gold()
        }))
        
        try:
            user_data = get_user_data(context.author.id)
            # if 24 hours has not gone by
            if user_data['claimed_daily_reward_time'] and time.time() - user_data['claimed_daily_reward_time'] < 60 * 60 * 24:
                time_remaining_text = ''
                seconds = (60 * 60 * 24) - math.floor(time.time() - user_data['claimed_daily_reward_time'])
                if seconds < 60:
                    time_remaining_text = f'{seconds} second(s)'
                else:
                    minutes = math.floor(seconds / 60)
                    if minutes < 60:
                        time_remaining_text = f'{minutes} minute(s)'
                    else:
                        hours = math.floor(minutes / 60)
                        time_remaining_text = f'{hours} hour(s)'

                await response.edit(embed=create_embed({
                    'title': f'You must wait {time_remaining_text} to claim your daily reward',
                    'color': discord.Color.red()
                }))
                return
            
            guild_settings = get_guild_data(context.guild.id)
            user_data['claimed_daily_reward_time'] = round(time.time())
            user_data['points'] += guild_settings['daily_reward']
            save_user_data(user_data)

            await response.edit(embed = create_embed({
                'title': f'You claimed your daily reward',
                'color': discord.Color.green()
            }))
        except Exception as error_message:
            await response.edit(embed = create_embed({
                'title': f'Could not claim daily reward',
                'color': discord.Color.red()
            }, {
                'Error Message': error_message
            }))
            
    @commands.command()
    async def leaderboard(self, context):
        response = await context.send(embed = create_embed({
            'title': f'Loading leaderboard...',
            'color': discord.Color.gold()
        }))

        try:
            users = {}
            for user_data in get_all_user_data('points'):
                if context.guild:
                    member = context.guild.get_member(user_data['user_id'])
                    if member:
                        users[member.name] = user_data['points']
                else:
                    user = self.client.get_user(user_data['user_id'])
                    if user:
                        users[user.name] = user_data['points']

            fields = {}
            users = sort_dictionary(users, True)
            for rank, member_name in enumerate(users):
                points = users.get(member_name)
                fields[f'{rank + 1}. {member_name}'] = f'{points} points'
                
                if rank == MAX_LEADERBOARD_FIELDS - 1:
                    break
        
            await response.edit(embed = create_embed({
                'title': 'Leaderboard'
            }, fields))
        except Exception as error_message:
            await response.edit(embed = create_embed({
                'title': f'Could not load leaderboard',
                'color': discord.Color.red()
            }, {
                'Error Message': error_message
            }))
        
    @commands.command()
    @commands.guild_only()
    async def qotd(self, context, *, aotd=None):
        if not aotd:
            await context.send(embed=create_embed({
                'title': 'You did not enter an answer for the QOTD',
                'color': discord.Color.red(),
            }))
            return

        user_data = get_user_data(context.author.id)
        if user_data['answered_qotd']:
            await context.send(embed=create_embed({
                'title': 'You already answered the QOTD',
                'color': discord.Color.red(),
            }))
            return

        guild_data = get_guild_data(context.guild.id)
        points_to_give = guild_data['points_per_aotd']

        user_data['answered_qotd'] = True
        user_data['points'] += points_to_give
        save_user_data(user_data)

        await context.send(embed = create_embed({
            'title': f'You earned {points_to_give} points for answering the QOTD',
        }))

    @commands.command()
    @commands.check(check_if_bot_manager)
    @commands.guild_only()
    async def resetqotd(self, context):
        response = await context.send(embed=create_embed({
            'title': 'Are you sure you want to manually reset everyone\'s QOTD status',
            'description': 'Members would be able to earn points by running ?qotd without an actual QOTD being published',
            'color': discord.Color.gold()
        }))

        try:
            await response.add_reaction(ACCEPT_EMOJI)
            reaction, user = await wait_for_reaction(self.client, context, ACCEPT_EMOJI)
            if not reaction:
                await response.edit(embed=create_embed({
                    'title': 'Process canceled',
                    'color': discord.Color.red()
                }))
                return

            await response.edit(embed = create_embed({
                'title': 'Resetting QOTD...',
                'color': discord.Color.green()
            }))

            for user_data in get_all_user_data():
                if context.guild.get_member(user_data['user_id']):
                    user_id = user_data['user_id']
                    print(f'Resetted {user_id}\'s QOTD status')
                    user_data['answered_qotd'] = False
                    save_user_data(user_data)
        except Exception as error_message:
            await response.edit(embed=create_embed({
                'title': 'Could not reset QOTD',
                'color': discord.Color.red()
            }, {
                'Error Message': error_message,
            }))

def setup(client):
    client.add_cog(points(client))
