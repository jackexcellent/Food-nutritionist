import os
import tempfile
import json
from datetime import datetime

import discord
from discord.ext import commands
from discord.ui import View

from image_recognition import analyze_food
from llm_gemini import generate_diet_recommendation, answer_question

# 模擬營養數據（image_recognition 只回傳標籤，這裡用模擬營養資料）
MOCK_NUTRITION = {
    "pizza": {"calories": 800, "carbs": 100, "protein": 30, "fat": 35},
    "burger": {"calories": 600, "carbs": 50, "protein": 25, "fat": 30},
    "salad": {"calories": 200, "carbs": 20, "protein": 10, "fat": 15},
    "default": {"calories": 500, "carbs": 60, "protein": 20, "fat": 25},
}

# 全域狀態
PENDING = {}  # user_id -> {step, user_name, height}

# 檔案路徑
ROOT = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
USER_LOG_FILE = os.path.join(ROOT, "user_log.json")


def load_user_logs():
    if os.path.exists(USER_LOG_FILE):
        with open(USER_LOG_FILE, "r", encoding="utf-8") as f:
            return json.load(f)
    return {}


def save_user_logs(logs):
    with open(USER_LOG_FILE, "w", encoding="utf-8") as f:
        json.dump(logs, f, indent=2, ensure_ascii=False)


def ensure_user_record(user_id, user_name):
    logs = load_user_logs()
    if user_id not in logs:
        logs[user_id] = {"user_name": user_name, "height": None, "weight": None, "foods": []}
        save_user_logs(logs)
        return True
    return False


def set_user_basic(user_id, user_name, height, weight):
    logs = load_user_logs()
    logs[user_id] = {"user_name": user_name, "height": height, "weight": weight, "foods": logs.get(user_id, {}).get("foods", [])}
    save_user_logs(logs)


def add_food_feedback(user_id, food_name, calories):
    logs = load_user_logs()
    if user_id not in logs:
        return
    logs[user_id].setdefault("foods", [])
    logs[user_id]["foods"].append({
        "food": food_name,
        "calories": calories,
        "timestamp": datetime.now().strftime("%Y-%m-%d %H:%M:%S"),
    })
    save_user_logs(logs)


HEIGHT_OPTIONS = [str(h) for h in range(150, 201, 5)]
WEIGHT_OPTIONS = [str(w) for w in range(40, 121, 5)]


class HeightSelect(View):
    def __init__(self, user_id: str, user_name: str):
        super().__init__(timeout=120)
        self.user_id = user_id
        self.user_name = user_name
        options = [discord.SelectOption(label=h, value=h) for h in HEIGHT_OPTIONS]
        self.add_item(discord.ui.Select(placeholder="請選擇身高(cm)", options=options, custom_id="height_select"))

    async def interaction_check(self, interaction: discord.Interaction) -> bool:
        return str(interaction.user.id) == self.user_id

    @discord.ui.select(custom_id="height_select")
    async def select_callback(self, select: discord.ui.Select, interaction: discord.Interaction):
        height = int(select.values[0])
        PENDING[self.user_id] = {"step": "weight", "user_name": self.user_name, "height": height}
        await interaction.response.send_message(f"已選擇身高 {height}cm，請接著選擇體重。", view=WeightSelect(self.user_id, self.user_name, height), ephemeral=True)


class WeightSelect(View):
    def __init__(self, user_id: str, user_name: str, height: int):
        super().__init__(timeout=120)
        self.user_id = user_id
        self.user_name = user_name
        self.height = height
        options = [discord.SelectOption(label=w, value=w) for w in WEIGHT_OPTIONS]
        self.add_item(discord.ui.Select(placeholder="請選擇體重(kg)", options=options, custom_id="weight_select"))

    async def interaction_check(self, interaction: discord.Interaction) -> bool:
        return str(interaction.user.id) == self.user_id

    @discord.ui.select(custom_id="weight_select")
    async def select_callback(self, select: discord.ui.Select, interaction: discord.Interaction):
        weight = float(select.values[0])
        set_user_basic(self.user_id, self.user_name, self.height, weight)
        PENDING.pop(self.user_id, None)
        await interaction.response.send_message(f"已記錄身高 {self.height}cm、體重 {weight}kg。", ephemeral=True)


class GoalSelect(View):
    def __init__(self, ctx: commands.Context):
        super().__init__(timeout=60)
        self.ctx = ctx
        options = [
            discord.SelectOption(label="健康飲食", value="healthy"),
            discord.SelectOption(label="減重飲食", value="weight_loss"),
        ]
        self.add_item(discord.ui.Select(placeholder="選擇分析目標", options=options, custom_id="goal_select"))

    async def interaction_check(self, interaction: discord.Interaction) -> bool:
        return interaction.user.id == self.ctx.author.id

    @discord.ui.select(custom_id="goal_select")
    async def select_callback(self, select: discord.ui.Select, interaction: discord.Interaction):
        goal = select.values[0]
        await interaction.response.defer()
        await analyze_main(self.ctx, goal)


class AskModal(discord.ui.Modal):
    def __init__(self):
        super().__init__(title="提問給食物營養師")
        self.question = discord.ui.TextInput(label="您的問題", style=discord.TextStyle.long, placeholder="請在此輸入您的問題...", required=True, max_length=500)
        self.add_item(self.question)

    async def on_submit(self, interaction: discord.Interaction):
        q = self.question.value.strip()
        # 使用 interaction 回覆並在後續把答案發到頻道
        await interaction.response.defer()
        try:
            answer = answer_question(q)
            embed = discord.Embed(title="💬 問題解答", description=answer, color=0x87CEEB)
            embed.add_field(name="問題", value=q, inline=False)
            await interaction.followup.send(embed=embed)
        except Exception as e:
            await interaction.followup.send(f"❌ 回答失敗：{e}")


class MainMenu(View):
    def __init__(self, ctx: commands.Context):
        super().__init__(timeout=60)
        self.ctx = ctx
        options = [
            discord.SelectOption(label="打招呼", value="hello"),
            discord.SelectOption(label="食物分析", value="analyze"),
            discord.SelectOption(label="問題詢問", value="ask"),
        ]
        self.add_item(discord.ui.Select(placeholder="選擇功能", options=options, custom_id="main_menu"))

    async def interaction_check(self, interaction: discord.Interaction) -> bool:
        return interaction.user.id == self.ctx.author.id

    @discord.ui.select(custom_id="main_menu")
    async def select_callback(self, select: discord.ui.Select, interaction: discord.Interaction):
        v = select.values[0]
        await interaction.response.defer()
        if v == "hello":
            await handle_hello(self.ctx)
        elif v == "analyze":
            await handle_analyze(self.ctx)
        elif v == "ask":
            # 打開 modal 讓使用者輸入問題
            await interaction.response.send_modal(AskModal())


async def analyze_main(ctx: commands.Context, goal: str):
    await ctx.send("圖片收到，分析中...🔍")
    if not ctx.message.attachments:
        await ctx.send("⚠️ 請在訊息中附上食物圖片（PNG/JPG/JPEG）。")
        return
    attachment = ctx.message.attachments[0]
    if not attachment.filename.lower().endswith(("png", "jpg", "jpeg")):
        await ctx.send("⚠️ 請上傳 PNG、JPG 或 JPEG 格式的圖片！")
        return
    try:
        with tempfile.NamedTemporaryFile(delete=False, suffix=os.path.splitext(attachment.filename)[1]) as temp_file:
            await attachment.save(temp_file.name)
            temp_file_path = temp_file.name
        try:
            food_results = analyze_food(temp_file_path, is_url=False)
            if not food_results:
                await ctx.send("⚠️ 未辨識到任何食物，請試試其他照片！")
                return
        finally:
            try:
                os.unlink(temp_file_path)
            except Exception:
                pass

        nutrition_summary = []
        for food, prob in sorted(food_results.items(), key=lambda x: x[1], reverse=True)[:2]:
            nutrition = MOCK_NUTRITION.get(food.lower(), MOCK_NUTRITION["default"])
            nutrition_summary.append({
                "food": food,
                "calories": nutrition["calories"],
                "carbs": nutrition["carbs"],
                "protein": nutrition["protein"],
                "fat": nutrition["fat"],
            })
        try:
            recommendation = generate_diet_recommendation(nutrition_summary, goal)
        except Exception as e:
            recommendation = f"生成建議錯誤：{str(e)}"

        user_id = str(ctx.author.id)
        for item in nutrition_summary:
            add_food_feedback(user_id, item["food"], item["calories"])

        embed = discord.Embed(title="🍱 食物辨識與飲食建議", description="以下是圖片的食物辨識結果與飲食建議：", color=0xFFA07A)
        recognition_text = "\n".join([f"{food}: {prob:.2%}" for food, prob in sorted(food_results.items(), key=lambda x: x[1], reverse=True)[:2]])
        embed.add_field(name="🔍 辨識結果", value=recognition_text, inline=False)
        for item in nutrition_summary:
            embed.add_field(
                name=f"📊 {item['food']} 營養",
                value=f"熱量: {item['calories']} kcal\n碳水化合物: {item['carbs']}g\n蛋白質: {item['protein']}g\n脂肪: {item['fat']}g",
                inline=True,
            )
        embed.add_field(name=f"{'健康' if goal == 'healthy' else '瘦身'}建議", value=recommendation, inline=False)
        embed.set_footer(text="由食物營養師為您分析 ✨")
        await ctx.send(embed=embed)
    except Exception as e:
        await ctx.send(f"❌ 發生錯誤：{str(e)}")


async def handle_hello(ctx: commands.Context):
    ensure_user_record(str(ctx.author.id), ctx.author.name)
    await ctx.send(f"嗨 {ctx.author.name}，我是你的食物營養師！")


async def handle_analyze(ctx: commands.Context):
    ensure_user_record(str(ctx.author.id), ctx.author.name)
    logs = load_user_logs()
    user = logs.get(str(ctx.author.id), {})
    if user.get("height") is None or user.get("weight") is None:
        PENDING[str(ctx.author.id)] = {"step": "height", "user_name": ctx.author.name}
        await ctx.send("請先提供基本資料：", view=HeightSelect(str(ctx.author.id), ctx.author.name))
        return
    await ctx.send("請選擇分析目標：", view=GoalSelect(ctx))


async def handle_ask(ctx: commands.Context, question: str | None = None):
    ensure_user_record(str(ctx.author.id), ctx.author.name)
    if not question:
        # 直接開啟 Modal
        return await ctx.send("請使用主選單的「問題詢問」或在指令後加上問題。")
    await ctx.send("正在查詢，請稍候...🤔")
    try:
        answer = answer_question(question)
        embed = discord.Embed(title="💬 問題解答", description=answer, color=0x87CEEB)
        embed.add_field(name="問題", value=question, inline=False)
        await ctx.send(embed=embed)
    except Exception as e:
        await ctx.send(f"❌ 回答失敗：{e}")


def register_commands(bot: commands.Bot):
    @bot.event
    async def on_ready():
        print(f"{bot.user} 上線啦！")

    @bot.event
    async def on_message(message: discord.Message):
        # ignore bots
        if message.author.bot:
            return
        user_id = str(message.author.id)
        # fallback numeric input for pending height/weight
        if user_id in PENDING:
            info = PENDING[user_id]
            if info.get("step") == "height":
                try:
                    height = int(message.content.strip())
                    PENDING[user_id] = {"step": "weight", "user_name": info["user_name"], "height": height}
                    await message.channel.send("已記錄身高，請選擇體重：", view=WeightSelect(user_id, info["user_name"], height))
                    return
                except Exception:
                    pass
            elif info.get("step") == "weight":
                try:
                    weight = float(message.content.strip())
                    set_user_basic(user_id, info["user_name"], info["height"], weight)
                    PENDING.pop(user_id, None)
                    await message.channel.send(f"已記錄身高 {info['height']}cm、體重 {weight}kg。")
                    return
                except Exception:
                    pass
        # main menu trigger: single slash
        if message.content.strip() == "/":
            await message.channel.send("請選擇功能：", view=MainMenu(message))
            return
        await bot.process_commands(message)

    # legacy prefix commands kept for backward compatibility
    @bot.command(name="hello")
    async def _hello(ctx: commands.Context):
        await handle_hello(ctx)

    @bot.command(name="analyze")
    async def _analyze(ctx: commands.Context):
        await handle_analyze(ctx)

    @bot.command(name="ask")
    async def _ask(ctx: commands.Context, *, question: str | None = None):
        if question is None:
            # open modal via interaction if available, otherwise prompt
            if ctx.interaction:
                await ctx.interaction.response.send_modal(AskModal())
            else:
                await ctx.send("請使用主選單或在指令後加上問題。")
            return
        await handle_ask(ctx, question)

    # register application (slash) commands so Discord shows them when user types '/'
    @bot.tree.command(name="hello", description="打招呼 - 與營養師互動")
    async def slash_hello(interaction: discord.Interaction):
        await interaction.response.defer()
        await handle_hello(await interaction.client.get_context(interaction.message) if interaction.message else interaction)

    @bot.tree.command(name="analyze", description="上傳食物圖片進行分析")
    async def slash_analyze(interaction: discord.Interaction):
        # respond with guidance; user should attach image in follow-up message
        await interaction.response.send_message("請在此訊息附上食物圖片，或在頻道中發送帶圖的訊息來分析。", ephemeral=True)

    @bot.tree.command(name="ask", description="向營養師提問")
    async def slash_ask(interaction: discord.Interaction):
        # open modal directly
        await interaction.response.send_modal(AskModal())
