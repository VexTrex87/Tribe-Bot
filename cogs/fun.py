from attr import dataclass
import discord
from discord.ext import commands
import time
import random
import aiohttp
import html

from helper import create_embed, wait_for_reaction
from constants import EIGHTBALL_RESPONSES, TRIVIA_URL, NUMBER_EMOJIS

async def trivia(amount, difficulty, type):
    async with aiohttp.ClientSession() as session:
        url = TRIVIA_URL.format(amount, difficulty, type)
        async with session.get(url) as r:
            if r.status == 200:
                results = await r.json()
                results = results['results'][0]
                data = {
                    'Category': results['category'],
                    'Type': results['type'],
                    'Difficulty': results['difficulty'],
                    'Question':results['question'],
                    'Correct_Answer': results['correct_answer'],
                    'Incorrect_Answers': results['incorrect_answers'],
                }

                for name, value in data.items():
                    if name == 'Incorrect_Answers':
                        value = [html.unescape(item) for item in value]
                    data[name] = html.unescape(value)
                return data

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

    @commands.command()
    async def trivia(self, context):
        response = await context.send(embed=create_embed({
            'title': 'Loading trivia question...',
            'color': discord.Color.gold()
        }))

        try:
            data = await trivia(1, 'easy', 'multiple')
            correct_answer = data['Correct_Answer']
            answers = [correct_answer] + data['Incorrect_Answers']

            formatted_answers = []
            for index, question in enumerate(answers):
                formatted_answers.append(f'{index + 1}. {question}')
                await response.add_reaction(NUMBER_EMOJIS[index])

            await response.edit(embed=create_embed({
                'title': data['Question'],
                "Description": 'Answer in 60 seconds',
            }, {
                data['Category']: '\n'.join(formatted_answers),
            }))

            reaction, user = await wait_for_reaction(self.client, context, emoji=NUMBER_EMOJIS, timeout=60)
            await response.clear_reactions()
            
            index = NUMBER_EMOJIS.index(reaction.emoji)
            if answers[index] == correct_answer:
                await response.edit(embed=create_embed({
                    'title': 'Correct: ' + data['Question'],
                    'color': discord.Color.green()
                }, {
                    data['Category']: '\n'.join(formatted_answers)
                }))
            else:
                await response.edit(embed=create_embed({
                    'title': 'Incorrect: ' + data['Question'],
                    'color': discord.Color.red(),
                    'footer': f'Correct Answer: {correct_answer}'
                }, {
                    data['Category']: '\n'.join(formatted_answers)
                }))

        except Exception as error_message:
            await response.edit(embed=create_embed({
                'title': 'Could not load trivia question',
                'color': discord.Color.red()
            }, {
                'Error Message': error_message
            }))

def setup(client):
    client.add_cog(fun(client))
