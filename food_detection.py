from ultralytics import YOLO
import cv2

# 載入模型
model = YOLO("best.pt")  # 確保檔案存在於同資料夾

# 讀取圖片
image_path = "apple1.jpg"  # 替換為你的圖片檔名
image = cv2.imread(image_path)

# 進行預測
results = model(image)

# 顯示結果（取出第一張圖的結果）
results[0].show()