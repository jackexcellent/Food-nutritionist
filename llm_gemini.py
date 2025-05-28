# import json
# import os
# import google as genai

# # Gemini API 配置
# # GEMINI_API_KEY = os.environ.get("GEMINI_API_KEY", "AIzaSyAu2-zO04EA_UPy_xJ568hnOc9JUgBlbMI")  
# # genai.configure(api_key=GEMINI_API_KEY)
# client = genai.Client(api_key="AIzaSyAu2-zO04EA_UPy_xJ568hnOc9JUgBlbMI")

# # 本地快取檔案
# RECOMMENDATION_CACHE_FILE = "recommendation_cache.json"

# # 初始化快取檔案
# if not os.path.exists(RECOMMENDATION_CACHE_FILE):
#     with open(RECOMMENDATION_CACHE_FILE, "w") as f:
#         json.dump({}, f)

# def generate_diet_recommendation(nutrition_summary, goal="healthy"):
#     """
#     使用 Google Gemini API 生成飲食建議，優化為繁體中文和台灣飲食文化。
    
#     Args:
#         nutrition_summary (list): 營養分析結果，包含食物名稱和營養數據。
#         goal (str): 目標，"healthy" 或 "weight_loss"。
    
#     Returns:
#         str: 飲食建議，或錯誤訊息。
#     """
#     # 檢查 API 密鑰
#     if not GEMINI_API_KEY or GEMINI_API_KEY == "YOUR_GEMINI_API_KEY":
#         return "錯誤：未找到 GEMINI_API_KEY，請設置環境變數或檢查程式碼。"
    
#     # 構建提示
#     prompt = (
#         "你是專精台灣飲食的營養師，使用繁體中文，語氣親切，符合台灣年輕人口味。根據以下餐點分析，提供100字內的飲食建議，"
#         "考慮台灣常見食物如滷肉飯、珍珠奶茶、牛肉麵，並避免高糖高脂飲食。\n"
#         "餐點分析：\n"
#     )
#     for item in nutrition_summary:
#         prompt += f"- {item['food']}：{item['calories']} kcal，{item['carbs']}g 澱粉，{item['protein']}g 蛋白質，{item['fat']}g 脂肪\n"
#     if goal == "healthy":
#         prompt += "建議如何平衡今日剩餘飲食，保持健康，考慮台灣飲食習慣。"
#     elif goal == "weight_loss":
#         prompt += "根據這餐早餐，建議減重飲食計劃，考慮台灣飲食習慣。"

#     # 檢查快取
#     with open(RECOMMENDATION_CACHE_FILE, "r") as f:
#         cache = json.load(f)
#     cache_key = f"{prompt}_{goal}"
#     if cache_key in cache:
#         return cache[cache_key]

#     # Gemini API 呼叫
#     try:
#         response = client.models.generate_content(
#             model="gemini-2.0-flash",
#             contents=prompt,
#         )
#         recommendation = response.text

#         # 儲存到快取
#         cache[cache_key] = recommendation
#         with open(RECOMMENDATION_CACHE_FILE, "w") as f:
#             json.dump(cache, f, indent=2)

#         return recommendation
#     except Exception as e:
#         return f"Gemini API 錯誤：{str(e)}"








import json
import os
import google.generativeai as genai
from dotenv import load_dotenv

# # 載入環境變數
# load_dotenv()

# # 嘗試載入 api.env 或 .env
# env_file = "api.env" if os.path.exists("api.env") else ".env"
# if not load_dotenv(env_file):
#     raise FileNotFoundError(f"錯誤：無法找到 {env_file} 檔案，請確認檔案存在於 food_bot 目錄。")

# Gemini API 配置
# GEMINI_API_KEY = os.getenv("GEMINI_API_KEY")
GEMINI_API_KEY = "AIzaSyAu2-zO04EA_UPy_xJ568hnOc9JUgBlbMI"
if not GEMINI_API_KEY:
    raise ValueError("錯誤：未找到 GEMINI_API_KEY，請在 .env 檔案中設置或提供有效的 API Key。")

genai.configure(api_key=GEMINI_API_KEY)

# 本地快取檔案
RECOMMENDATION_CACHE_FILE = "recommendation_cache.json"

# 初始化快取檔案
if not os.path.exists(RECOMMENDATION_CACHE_FILE):
    with open(RECOMMENDATION_CACHE_FILE, "w", encoding="utf-8") as f:
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
        prompt += f"- {item['food']}：{item['calories']} kcal，{item['carbs']}g 碳水化合物，{item['protein']}g 蛋白質，{item['fat']}g 脂肪\n"
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
        model = genai.GenerativeModel("gemini-1.5-pro")
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