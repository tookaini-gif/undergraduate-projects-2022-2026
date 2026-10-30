from ultralytics import YOLO
import os
import pandas as pd
from pathlib import Path

class WeedDetector:
    def __init__(self, model_path='best.pt'):
        self.model = YOLO(model_path)  # Load the pre-trained model directly
        
    def predict(self, image_path, conf=0.25):
        """预测单张图片"""
        results = self.model.predict(
            source=image_path,
            conf=conf,
            save=True  # Save the prediction images (optional)
        )
        return results
    
    def evaluate_and_save(self, val_folder, output_csv, conf=0.25):
        """
        对验证集进行检测并保存结果到CSV文件
        """
        if self.model is None:
            raise ValueError("请先加载模型！")
        
        results_list = []
        results = self.model.predict(source=val_folder, conf=conf, save=True)
        
        # 处理每张图片的预测结果
        for result in results:
            img_path = Path(result.path).name
            boxes = result.boxes
            
            if len(boxes) > 0:
                for box in boxes:
                    class_id = box.cls.item()
                    
                    # 计算宽度和高度
                    x_min = round(box.xyxy[0][0].item(), 2)
                    y_min = round(box.xyxy[0][1].item(), 2)
                    width = round(box.xyxy[0][2].item() - x_min, 2)
                    height = round(box.xyxy[0][3].item() - y_min, 2)
                    
                    results_list.append({
                        'image_id': os.path.splitext(img_path)[0],
                        'class_id': int(class_id),  # 0表示作物，1表示杂草
                        'x_min': x_min,
                        'y_min': y_min,
                        'width': width,
                        'height': height,
                    })
        
        # 转换为DataFrame并添加ID列
        df = pd.DataFrame(results_list)
        df.index = range(1, len(df) + 1)  # 从1开始的索引
        df.index.name = 'ID'
        
        # 重排列顺序
        df = df[['image_id', 'class_id', 'x_min', 'y_min', 'width', 'height']]
        
        # 保存为CSV
        df.to_csv(output_csv)
        print(f"检测结果已保存到: {output_csv}")
        
        # 返回统计信息
        stats = {
            'total_images': len(set(df['image_id'])),
            'total_detections': len(df),
            'weed_count': len(df[df['class_id'] == 1]),
            'crop_count': len(df[df['class_id'] == 0])
        }
        return stats

def main():
    # 设置路径
    test_path = r"D:\WD\Weed_Detection_final\Weed_Detection\test\images"  # 验证集图片文件夹路径
    
    # 初始化检测器并加载预训练模型
    detector = WeedDetector(model_path='best.pt')
    
    # 预测验证集并保存结果到CSV
    stats = detector.evaluate_and_save(
        val_folder=test_path,  # 使用验证集路径
        output_csv='detection_results.csv',  # 指定CSV文件名
        conf=0.25
    )
    print("检测统计信息:", stats)

if __name__ == "__main__":
    main()
