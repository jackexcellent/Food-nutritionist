import discord
import os
import tempfile
import json
from datetime import datetime
from image_recognition import analyze_food
from llm_gemini import generate_diet_recommendation, answer_question

# 模擬營養數據（因為 image_recognition.py 僅提供標籤）
MOCK_NUTRITION = {
    "pizza": {"calories": 800, "carbs": 100, "protein": 30, "fat": 35},
    "burger": {"calories": 600, "carbs": 50, "protein": 25, "fat": 30},
    "salad": {"calories": 200, "carbs": 20, "protein": 10, "fat": 15},
    # 可擴展其他食物
    "default": {"calories": 500, "carbs": 60, "protein": 20, "fat": 25}
}

def register_commands(bot):
    # 使用者行為紀錄
    USER_LOG_FILE = os.path.join(os.path.dirname(os.path.dirname(os.path.abspath(__file__))), "user_log.json")

    # 暫存等待輸入的使用者資料
    pending_user_info = {}

    async def ask_height_weight(ctx, user_id, user_name):
        pending_user_info[user_id] = {"step": "height", "user_name": user_name}
        await ctx.send(f"{user_name}，歡迎使用食物營養師！請輸入您的身高（cm）")

    def save_user_basic(user_id, user_name, height, weight):
        if os.path.exists(USER_LOG_FILE):
            with open(USER_LOG_FILE, "r", encoding="utf-8") as f:
                logs = json.load(f)
        else:
            logs = {}
        logs[user_id] = {
            "user_name": user_name,
            "height": height,
            "weight": weight,
            "foods": []
        }
        with open(USER_LOG_FILE, "w", encoding="utf-8") as f:
            json.dump(logs, f, indent=2, ensure_ascii=False)

    def add_food_feedback(user_id, food_name, calories):
        if os.path.exists(USER_LOG_FILE):
            with open(USER_LOG_FILE, "r", encoding="utf-8") as f:
                logs = json.load(f)
        else:
            logs = {}
        if user_id not in logs:
            return
        logs[user_id].setdefault("foods", [])
        logs[user_id]["foods"].append({
            "food": food_name,
            "calories": calories,
            "timestamp": datetime.now().strftime("%Y-%m-%d %H:%M:%S")
        })
        with open(USER_LOG_FILE, "w", encoding="utf-8") as f:
            json.dump(logs, f, indent=2, ensure_ascii=False)

    def log_user_action(ctx, command_name):
        user_id = str(ctx.author.id)
        log_entry = {
            "user_name": ctx.author.name,
            "command": command_name,
            "timestamp": datetime.now().strftime("%Y-%m-%d %H:%M:%S")
        }
        try:
            if os.path.exists(USER_LOG_FILE):
                with open(USER_LOG_FILE, "r", encoding="utf-8") as f:
                    logs = json.load(f)
            else:
                logs = {}
            is_first = user_id not in logs
            if user_id not in logs:
                logs[user_id] = []
            logs[user_id].append(log_entry)
            with open(USER_LOG_FILE, "w", encoding="utf-8") as f:
                json.dump(logs, f, indent=2, ensure_ascii=False)
            # 第一次使用者，詢問身高
            if is_first:
                import asyncio
                asyncio.create_task(ask_height_weight(ctx, user_id, ctx.author.name))
        except Exception as e:
            print(f"[使用者紀錄錯誤] {e}")
    # 監聽訊息，處理身高體重輸入
    @bot.event
    async def on_message(message):
        user_id = str(message.author.id)
        # 機器人自己不處理
        if message.author.bot:
            return
        # 是否等待身高或體重
        if user_id in pending_user_info:
            info = pending_user_info[user_id]
            if info["step"] == "height":
                try:
                    height = int(message.content.strip())
                    info["height"] = height
                    info["step"] = "weight"
                    await message.channel.send(f"請輸入您的體重（kg）")
                except Exception:
                    await message.channel.send("格式錯誤，請輸入數字，例如：170")
                return
            elif info["step"] == "weight":
                try:
                    weight = float(message.content.strip())
                    info["weight"] = weight
                    # 寫入 user_log.json（只保留必要資訊）
                    save_user_basic(user_id, info["user_name"], info["height"], info["weight"])
                    await message.channel.send(f"已記錄您的身高 {info['height']}cm、體重 {info['weight']}kg！")
                    del pending_user_info[user_id]
                except Exception:
                    await message.channel.send("格式錯誤，請輸入數字，例如：65")
                return
        await bot.process_commands(message)
    @bot.event
    async def on_ready():
        print(f'{bot.user} 上線啦！')

    @bot.command()
    async def hello(ctx):
        log_user_action(ctx, "hello")
        await ctx.send(f'嗨嗨 {ctx.author.name}，我是你的食物營養師')

    @bot.command()
    async def analyze(ctx, goal="healthy"):
        log_user_action(ctx, "analyze")
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
                async def analyze(ctx, goal="healthy"):
                    log_user_action(ctx, "analyze")
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
        log_user_action(ctx, "ask")
        """
        回答用戶在 Discord 輸入的問題，使用 Gemini LLM。
        
        Args:
            ctx: Discord 上下文。
            question (str): 用戶的問題。
        """
        if not question:
                        user_id = str(ctx.author.id)
                        for item in nutrition_summary:
                            add_food_feedback(user_id, item["food"], item["calories"])
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