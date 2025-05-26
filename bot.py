import discord
from discord.ext import commands
import requests


intents = discord.Intents.default()
intents.message_content = True  # 這行要打開才能讀取訊息

bot = commands.Bot(command_prefix='!', intents=intents)

@bot.event
async def on_ready():
    print(f'{bot.user} 上線啦！')

@bot.command()
async def hello(ctx):
    await ctx.send(f'嗨嗨 {ctx.author.name}，我是你的食物營養師 💖')

bot.run('MTM1NTUyMjcxOTY1OTMzMTU5NA.GcVI2O.J4G4a68uF4DCTtMTrKYlPtfiKCZ9CXJN7CwELI')