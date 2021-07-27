from attr import dataclass
import discord
from discord.ext import commands
import time
import random
import aiohttp
import html

from helper import create_embed
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
            questions = [data['Correct_Answer']] + data['Incorrect_Answers']

            formatted_questions = []
            for index, question in enumerate(questions):
                formatted_questions.append(f'{index + 1}. {question}')
                await response.add_reaction(NUMBER_EMOJIS[index])

            await response.edit(embed=create_embed({
                'title': data['Question']
            }, {
                '\n'.join(formatted_questions): 'React to answer'
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
