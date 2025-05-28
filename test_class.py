from ultralytics import YOLO

# 載入模型
model = YOLO("food_detection.h5")  # 替換為你的模型檔案路徑

# 獲取類別名稱
class_names = model.names
print("模型可辨識的食物類別：", class_names)
print("類別數量：", len(class_names))