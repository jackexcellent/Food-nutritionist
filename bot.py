import discord
from discord.ext import commands
import requests
from dotenv import load_dotenv



intents = discord.Intents.default()
intents.message_content = True  # 這行要打開才能讀取訊息

bot = commands.Bot(command_prefix='!', intents=intents)

@bot.event
async def on_ready():
    print(f'{bot.user} 上線啦！')

@bot.command()
async def hello(ctx):
    await ctx.send(f'嗨嗨 {ctx.author.name}，我是你的食物營養師 💖')

load_dotenv()  # 讀取 .env 檔案
TOKEN = os.getenv("DISCORD_TOKEN")
bot.run(TOKEN)
