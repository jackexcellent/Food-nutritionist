import discord
from discord.ext import commands
import requests
from dotenv import load_dotenv
import os
from llm_gemini import generate_diet_recommendation

# 獲取當前腳本的目錄
BASE_DIR = os.path.dirname(os.path.abspath(__file__))

# 載入環境變數
env_file = os.path.join(BASE_DIR, "test.env" if os.path.exists(os.path.join(BASE_DIR, "test.env")) else ".env")
if not os.path.exists(env_file):
    raise FileNotFoundError(f"錯誤：無法找到 {env_file} 檔案，請確認檔案存在於 {BASE_DIR} 目錄。")
if not load_dotenv(env_file):
    raise RuntimeError(f"錯誤：無法載入 {env_file} 檔案，請檢查檔案格式或權限。")

intents = discord.Intents.default()
intents.message_content = True
bot = commands.Bot(command_prefix='!', intents=intents)

@bot.event
async def on_ready():
    print(f'{bot.user} 上線啦！')

@bot.command()
async def hello(ctx):
    await ctx.send(f'嗨嗨 {ctx.author.name}，我是你的食物營養師')

@bot.command()
async def analyze(ctx, goal="healthy"):
    """
    分析上傳的食物圖片，提供營養資訊和飲食建議。
    
    Args:
        ctx: Discord 上下文。
        goal (str): 目標，"healthy" 或 "weight_loss"。
    """
    if not ctx.message.attachments:
        await ctx.send("請上傳一張食物照片！")
        return

    if goal not in ["healthy", "weight_loss"]:
        await ctx.send("⚠️ 目標無效！請使用 `healthy` 或 `weight_loss`（例如：`!analyze weight_loss`）。")
        return

    await ctx.send("圖片收到，分析中...🔍")
    attachment = ctx.message.attachments[0]
    
    if not attachment.filename.lower().endswith(('png', 'jpg', 'jpeg')):
        await ctx.send("⚠️ 請上傳 PNG、JPG 或 JPEG 格式的圖片！")
        return

    image_bytes = await attachment.read()

    try:
        # 發送圖片到後端
        response = requests.post(
            'http://127.0.0.1:8000/analyze',
            files={'image': (attachment.filename, image_bytes)}
        )

        if response.status_code == 200:
            result = response.json()

            # 格式化營養數據以供 LLM 使用
            nutrition_summary = [{
                "food": "未知食物" if "food" not in result else result["food"],
                "calories": result.get("calories", 0),  # 修正可能的拼寫錯誤
                "carbs": result.get("carbs", 0),
                "protein": result.get("protein", 0),
                "fat": result.get("fat", 0)
            }]

            # 生成飲食建議
            try:
                recommendation = generate_diet_recommendation(nutrition_summary, goal)
            except Exception as e:
                recommendation = f"生成建議錯誤：{str(e)}"

            # 創建嵌入訊息
            embed = discord.Embed(
                title="🍱 食物營養分析",
                description="以下是這道食物的營養資訊與飲食建議：",
                color=0xFFA07A
            )
            embed.add_field(name="🔥 熱量", value=f"{result.get('calories', 0)} kcal", inline=True)
            embed.add_field(name="💪 蛋白質", value=f"{result.get('protein', 0)} g", inline=True)
            embed.add_field(name="🧈 脂肪", value=f"{result.get('fat', 0)} g", inline=True)
            embed.add_field(name="🍞 碳水化合物", value=f"{result.get('carbs', 0)} g", inline=True)
            embed.add_field(
                name=f"{'健康' if goal == 'healthy' else '瘦身'}建議",
                value=recommendation,
                inline=False
            )
            embed.add_field(text="由食物營養師為您分析 ✨")

            await ctx.send(embed=embed)
        else:
            await ctx.send(f"⚠️ 後端分析失敗（狀態碼：{response.status_code}）")
    except Exception as e:
        await ctx.send(f"❌ 發生錯誤：無法連線到後端伺服器\n錯誤資訊：`{str(e)}`")

# 運行 Bot
TOKEN = os.getenv("DISCORD_BOT_API_KEY")
if not TOKEN:
    raise ValueError("錯誤：未找到 DISCORD_BOT_API_KEY，請在 test.env 或 .env 檔案中設置。")
bot.run(TOKEN)