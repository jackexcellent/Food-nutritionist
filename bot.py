import discord
from discord.ext import commands
import requests
from dotenv import load_dotenv
import os


intents = discord.Intents.default()
intents.message_content = True  # 這行要打開才能讀取訊息

bot = commands.Bot(command_prefix='!', intents=intents)

@bot.event
async def on_ready():
    print(f'{bot.user} 上線啦！')

@bot.command()
async def hello(ctx):
    await ctx.send(f'嗨嗨 {ctx.author.name}，我是你的食物營養師')

@bot.event
async def on_message(message):
    if message.author == bot.user:
        return

    if message.attachments:
        for attachment in message.attachments:
            if attachment.filename.lower().endswith(('png', 'jpg', 'jpeg')):
                await message.channel.send("圖片收到，分析中...🔍")
                image_bytes = await attachment.read()

                try:
                    response = requests.post(
                        'http://127.0.0.1:8000/analyze',
                        files={'image': (attachment.filename, image_bytes)}
                    )

                    if response.status_code == 200:
                        result = response.json()

                        embed = discord.Embed(
                            title="🍱 食物營養分析",
                            description="以下是這道食物的營養資訊：",
                            color=0xFFA07A
                        )
                        embed.add_field(name="🔥 熱量", value=f"{result['calories']} kcal", inline=True)
                        embed.add_field(name="💪 蛋白質", value=f"{result['protein']} g", inline=True)
                        embed.add_field(name="🧈 脂肪", value=f"{result['fat']} g", inline=True)
                        embed.add_field(name="🍞 碳水化合物", value=f"{result['carbs']} g", inline=True)
                        embed.set_footer(text="由食物營養師為您分析 ✨")

                        await message.channel.send(embed=embed)
                    else:
                        await message.channel.send("⚠️ 後端分析失敗了 QQ")

                except Exception as e:
                    await message.channel.send(f"❌ 發生錯誤：無法連線到後端伺服器\n錯誤資訊：`{e}`")

    await bot.process_commands(message)

load_dotenv()  # 讀取 .env 檔案
TOKEN = os.getenv("DISCORD_TOKEN")
bot.run(TOKEN)
