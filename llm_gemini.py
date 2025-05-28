import json
import os
import google.generativeai as genai
from dotenv import load_dotenv

# 獲取當前腳本的目錄
BASE_DIR = os.path.dirname(os.path.abspath(__file__))

# 載入環境變數
env_file = os.path.join(BASE_DIR, "test.env" if os.path.exists(os.path.join(BASE_DIR, "test.env")) else ".env")
if not os.path.exists(env_file):
    raise FileNotFoundError(f"錯誤：無法找到 {env_file} 檔案，請確認檔案存在於 {BASE_DIR} 目錄。")
if not load_dotenv(env_file):
    raise RuntimeError(f"錯誤：無法載入 {env_file} 檔案，請檢查檔案格式或權限。")

# Gemini API 配置
GEMINI_API_KEY = os.getenv("GEMINI_API_KEY")
if not GEMINI_API_KEY:
    raise ValueError("錯誤：未找到 GEMINI_API_KEY，請在 test.env 或 .env 檔案中設置正確的 API Key。")

genai.configure(api_key=GEMINI_API_KEY)

# 本地快取檔案
RECOMMENDATION_CACHE_FILE = os.path.join(BASE_DIR, "recommendation_cache.json")
QUESTION_CACHE_FILE = os.path.join(BASE_DIR, "question_cache.json")

# 初始化快取檔案
if not os.path.exists(RECOMMENDATION_CACHE_FILE):
    with open(RECOMMENDATION_CACHE_FILE, "w", encoding="utf-8") as f:
        json.dump({}, f)
if not os.path.exists(QUESTION_CACHE_FILE):
    with open(QUESTION_CACHE_FILE, "w", encoding="utf-8") as f:
        json.dump({}, f)

def generate_diet_recommendation(nutrition_summary, goal="healthy"):
    """
    使用 Google Gemini API 生成飲食建議，優化為繁體中文和台灣飲食文化。
    
    Args:
        nutrition_summary (list): 營養分析結果，包含食物名稱和營養數據。
        goal (str): 目標，"healthy" 或 "weight_loss"。
    
    Returns:
        str: 飲食建議，或錯誤訊息。
    """
    # 構建提示
    prompt = (
        "你是專精台灣飲食的營養師，使用繁體中文，語氣親切，適合台灣年輕人。根據以下餐點分析，提供100字內的飲食建議，"
        "考慮台灣常見食物如滷肉飯、珍珠奶茶、牛肉麵，並避免高糖高脂飲食。\n"
        "餐點分析：\n"
    )
    for item in nutrition_summary:
        # 處理可能的缺失營養數據
        calories = item.get("calories", "未知")
        carbs = item.get("carbs", "未知")
        protein = item.get("protein", "未知")
        fat = item.get("fat", "未知")
        prompt += f"- {item['food']}：熱量 {calories} kcal，碳水化合物 {carbs}g，蛋白質 {protein}g，脂肪 {fat}g\n"
    if goal == "healthy":
        prompt += "建議如何平衡今日剩餘飲食，保持健康，考慮台灣飲食習慣。"
    elif goal == "weight_loss":
        prompt += "根據這餐早餐，建議減重飲食計畫，考慮台灣飲食習慣。"

    # 檢查快取
    with open(RECOMMENDATION_CACHE_FILE, "r", encoding="utf-8") as f:
        cache = json.load(f)
    cache_key = f"{prompt}_{goal}"
    if cache_key in cache:
        return cache[cache_key]

    # Gemini API 呼叫
    try:
        model = genai.GenerativeModel("gemini-2.0-flash")
        response = model.generate_content(
            prompt,
            generation_config={
                "max_output_tokens": 100,
                "temperature": 0.7
            }
        )
        recommendation = response.text.strip()

        # 儲存到快取
        cache[cache_key] = recommendation
        with open(RECOMMENDATION_CACHE_FILE, "w", encoding="utf-8") as f:
            json.dump(cache, f, indent=2, ensure_ascii=False)

        return recommendation
    except Exception as e:
        return f"Gemini API 錯誤：{str(e)}"

def answer_question(question):
    """
    使用 Google Gemini API 回答用戶問題，優化為繁體中文，適合台灣年輕人。
    
    Args:
        question (str): 用戶輸入的問題。
    
    Returns:
        str: 回答，或錯誤訊息。
    """
    # 構建提示
    prompt = (
        "你是一位知識淵博的助手，專精台灣文化，使用繁體中文，語氣親切，適合台灣年輕人。請回答以下問題，答案簡潔且不超過150字：\n"
        f"問題：{question}"
    )

    # 檢查快取
    with open(QUESTION_CACHE_FILE, "r", encoding="utf-8") as f:
        cache = json.load(f)
    cache_key = f"{prompt}"
    if cache_key in cache:
        return cache[cache_key]

    # Gemini API 呼叫
    try:
        model = genai.GenerativeModel("gemini-2.0-flash")
        response = model.generate_content(
            prompt,
            generation_config={
                "max_output_tokens": 150,
                "temperature": 0.7
            }
        )
        answer = response.text.strip()

        # 儲存到快取
        cache[cache_key] = answer
        with open(QUESTION_CACHE_FILE, "w", encoding="utf-8") as f:
            json.dump(cache, f, indent=2, ensure_ascii=False)

        return answer
    except Exception as e:
        return f"Gemini API 錯誤：{str(e)}"