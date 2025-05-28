from ultralytics import YOLO

# 載入模型
model = YOLO("yolov8n.pt")  # 替換為你的 .pt 檔案路徑

# 獲取類別名稱
class_names = model.names
print("模型可辨識的食物類別：", class_names)
print("類別數量：", len(class_names))