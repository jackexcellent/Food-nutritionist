import discord
import os
from discord.ext import commands
from core.discord_handler import register_commands

def main():
    intents = discord.Intents.default()
    intents.message_content = True
    bot = commands.Bot(command_prefix='!', intents=intents)

    register_commands(bot) 

    # 運行 Bot
    TOKEN = os.getenv("DISCORD_BOT_API_KEY")
    if not TOKEN:
        raise ValueError("錯誤：未找到 DISCORD_BOT_API_KEY，請在 test.env 或 .env 檔案中設置。")
    bot.run(TOKEN)
    
    
if __name__ == "__main__":
    main()