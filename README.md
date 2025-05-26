# Food-nutritionist
# 這是我們的專題 :))

檔案結構 :

food_bot/
├── discord_bot.py
├── image_recognition.py
├── llm_groq.py
├── nutrition_cache.json
├── recommendation_cache.json

功能分工 :

    discord_bot.py：接收用戶上傳的照片，調用 image_recognition.py 進行辨識，查詢 Edamam API 獲取營養數據，調用 llm_groq.py 生成建議，並回傳結果。

    image_recognition.py：處理照片，運行 nateraw/food 模型，返回食物標籤和機率。

    llm_groq.py：使用 Groq API 生成飲食建議，優化提示以支援繁體中文和台灣飲食文化，包含快取機制減少 API 呼叫。

    HIIII