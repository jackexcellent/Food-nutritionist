from PIL import Image
import io
import requests
from transformers import AutoModelForImageClassification, AutoProcessor
import torch
import os

# 載入圖像辨識模型
image_model = AutoModelForImageClassification.from_pretrained("nateraw/food")
image_processor = AutoProcessor.from_pretrained("nateraw/food")

def analyze_food(image_source, food_labels=None, is_url=True, threshold=0.05):
    """
    使用 nateraw/food 模型分析食物照片，返回高機率食物標籤。
    
    Args:
        image_source (str): 圖片 URL 或本地檔案路徑。
        food_labels (list): 食物標籤列表（可選，若為 None 則使用模型預設標籤）。
        is_url (bool): True 表示 image_source 是 URL，False 表示本地檔案路徑。
        threshold (float): 機率閾值，僅返回高於此值的標籤。
    
    Returns:
        dict: 食物標籤和機率，例如 {"pizza": 0.8, "burger": 0.15}。
    """
    try:
        # 處理圖片
        if is_url:
            response = requests.get(image_source)
            response.raise_for_status()
            image = Image.open(io.BytesIO(response.content)).convert("RGB")
        else:
            if not os.path.exists(image_source):
                raise FileNotFoundError(f"本地圖片 {image_source} 不存在")
            image = Image.open(image_source).convert("RGB")
        
        inputs = image_processor(images=image, return_tensors="pt")

        # 模型推理
        device = "cuda" if torch.cuda.is_available() else "cpu"
        with torch.no_grad():  # 不用梯度計算 節省資源
            outputs = image_model(**inputs.to(device))
        probs = outputs.logits.softmax(dim=1)

        # 使用模型預設標籤或自定義標籤
        if food_labels is None:
            food_labels = list(image_model.config.id2label.values())
        
        # 僅返回高於閾值的標籤
        return {label: prob.item() for label, prob in zip(food_labels, probs[0]) if prob.item() > threshold}
    except Exception as e:
        raise Exception(f"圖像辨識錯誤：{str(e)}")