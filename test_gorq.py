# import json
# import os
# from groq import Groq

# # Groq API 配置
# GROQ_API_KEY = "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"
# groq_client = Groq(api_key=GROQ_API_KEY)

# # 本地快取檔案
# RECOMMENDATION_CACHE_FILE = "recommendation_cache.json"

# # 初始化快取檔案
# if not os.path.exists(RECOMMENDATION_CACHE_FILE):
#     with open(RECOMMENDATION_CACHE_FILE, "w") as f:
#         json.dump({}, f)

# def generate_diet_recommendation(nutrition_summary, goal="healthy"):
#     """
#     使用 Groq API 生成飲食建議，優化為繁體中文和台灣飲食文化。
    
#     Args:
#         nutrition_summary (list): 營養分析結果，包含食物名稱和營養數據。
#         goal (str): 目標，"healthy" 或 "weight_loss"。
    
#     Returns:
#         str: 飲食建議，或錯誤訊息。
#     """
#     # 構建提示
#     prompt = (
#         "你是專精台灣飲食的營養師，使用繁體中文。根據以下餐點分析，提供詳細飲食建議，"
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

#     # Groq API 呼叫
#     try:
#         response = groq_client.chat.completions.create(
#             model="llama-3.1-8b-instant",
#             messages=[
#                 {"role": "system", "content": "你是專精台灣飲食的營養師，使用繁體中文。"},
#                 {"role": "user", "content": prompt}
#             ],
#             max_tokens=200,
#             temperature=0.7
#         )
#         recommendation = response.choices[0].message.content

#         # 儲存到快取
#         cache[cache_key] = recommendation
#         with open(RECOMMENDATION_CACHE_FILE, "w") as f:
#             json.dump(cache, f, indent=2)

#         return recommendation
#     except Exception as e:
#         return f"Groq API 錯誤：{str(e)}"



from google import genai

client = genai.Client(api_key="AIzaSyAu2-zO04EA_UPy_xJ568hnOc9JUgBlbMI")

response = client.models.generate_content(
    model="gemini-2.0-flash", contents="what is life's meaning?",
)
print(response.text)