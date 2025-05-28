import discord
from discord.ext import commands
from dotenv import load_dotenv
import os
import tempfile
from image_recognition import analyze_food
from llm_gemini import generate_diet_recommendation, answer_question

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

# 模擬營養數據（因為 image_recognition.py 僅提供標籤）
MOCK_NUTRITION = {
    "pizza": {"calories": 800, "carbs": 100, "protein": 30, "fat": 35},
    "burger": {"calories": 600, "carbs": 50, "protein": 25, "fat": 30},
    "salad": {"calories": 200, "carbs": 20, "protein": 10, "fat": 15},
    # 可擴展其他食物
    "default": {"calories": 500, "carbs": 60, "protein": 20, "fat": 25}
}

@bot.event
async def on_ready():
    print(f'{bot.user} 上線啦！')

@bot.command()
async def hello(ctx):
    await ctx.send(f'嗨嗨 {ctx.author.name}，我是你的食物營養師')

@bot.command()
async def analyze(ctx, goal="healthy"):
    """
    分析上傳的食物圖片，提供辨識結果和飲食建議。
    
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

    try:
        # 保存圖片到臨時檔案
        with tempfile.NamedTemporaryFile(delete=False, suffix=".jpg") as temp_file:
            await attachment.save(temp_file.name)
            temp_file_path = temp_file.name

        # 圖像辨識
        try:
            food_results = analyze_food(temp_file_path, is_url=False)
            if not food_results:
                await ctx.send("⚠️ 未辨識到任何食物，請試試其他照片！")
                return
        finally:
            # 清理臨時檔案
            os.unlink(temp_file_path)

        # 格式化營養數據
        nutrition_summary = []
        for food, prob in sorted(food_results.items(), key=lambda x: x[1], reverse=True)[:2]:  # 取前兩個高機率食物
            nutrition = MOCK_NUTRITION.get(food.lower(), MOCK_NUTRITION["default"])
            nutrition_summary.append({
                "food": food,
                "calories": nutrition["calories"],
                "carbs": nutrition["carbs"],
                "protein": nutrition["protein"],
                "fat": nutrition["fat"]
            })

        # 生成飲食建議
        try:
            recommendation = generate_diet_recommendation(nutrition_summary, goal)
        except Exception as e:
            recommendation = f"生成建議錯誤：{str(e)}"

        # 創建嵌入訊息
        embed = discord.Embed(
            title="🍱 食物辨識與飲食建議",
            description="以下是圖片的食物辨識結果與飲食建議：",
            color=0xFFA07A
        )
        # 顯示辨識結果
        recognition_text = "\n".join([f"{food}: {prob:.2%}" for food, prob in sorted(food_results.items(), key=lambda x: x[1], reverse=True)[:2]])
        embed.add_field(name="🔍 辨識結果", value=recognition_text, inline=False)
        # 顯示營養數據
        for item in nutrition_summary:
            embed.add_field(
                name=f"📊 {item['food']} 營養",
                value=f"熱量: {item['calories']} kcal\n碳水化合物: {item['carbs']}g\n蛋白質: {item['protein']}g\n脂肪: {item['fat']}g",
                inline=True
            )
        # 顯示建議
        embed.add_field(
            name=f"{'健康' if goal == 'healthy' else '瘦身'}建議",
            value=recommendation,
            inline=False
        )
        embed.set_footer(text="由食物營養師為您分析 ✨")

        await ctx.send(embed=embed)
    except Exception as e:
        await ctx.send(f"❌ 發生錯誤：{str(e)}")

@bot.command()
async def ask(ctx, *, question):
    """
    回答用戶在 Discord 輸入的問題，使用 Gemini LLM。
    
    Args:
        ctx: Discord 上下文。
        question (str): 用戶的問題。
    """
    if not question:
        await ctx.send("⚠️ 請輸入問題！（例如：`!ask 如何健康飲食？`）")
        return

    await ctx.send("正在思考您的問題...🤔")
    try:
        answer = answer_question(question)
        embed = discord.Embed(
            title="💬 問題解答",
            description=answer,
            color=0x87CEEB
        )
        embed.add_field(name="問題", value=question, inline=False)
        embed.set_footer(text="由食物營養師助手回答 ✨")
        await ctx.send(embed=embed)
    except Exception as e:
        await ctx.send(f"❌ 回答問題時發生錯誤：{str(e)}")

# 運行 Bot
TOKEN = os.getenv("DISCORD_BOT_API_KEY")
if not TOKEN:
    raise ValueError("錯誤：未找到 DISCORD_BOT_API_KEY，請在 test.env 或 .env 檔案中設置。")
bot.run(TOKEN)