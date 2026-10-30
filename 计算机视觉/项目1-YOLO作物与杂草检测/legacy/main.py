from ultralytics import YOLO
import os
from pathlib import Path
import yaml
import shutil
import pandas as pd

class GrowingPointDetector:
    def __init__(self, data_yaml_path=None):
        self.model = None
        self.data_yaml_path = data_yaml_path
        
    def prepare_data_yaml(self, train_path, val_path, test_path=None, names=['weed', 'crop']):
        """准备数据配置文件"""
        data_dict = {
            'path': os.path.dirname(train_path),  # 数据集根目录
            'train': train_path,  # 训练集路径
            'val': val_path,      # 验证集路径
            'names': {i: name for i, name in enumerate(names)}  # 类别名称
        }
        
        if test_path:
            data_dict['test'] = test_path
            
        # 保存配置文件
        if not self.data_yaml_path:
            self.data_yaml_path = 'dataset.yaml'
            
        with open(self.data_yaml_path, 'w') as f:
            yaml.dump(data_dict, f)
            
    def train(self, epochs=100, imgsz=640, batch_size=8, device='cpu'):
        """训练模型"""
        # 初始化YOLOv8模型
        self.model = YOLO('best.pt')  # 使用预训练的YOLOv8 nano模型
        
        # 开始训练
        self.model.train(
            data=self.data_yaml_path,
            epochs=epochs,
            imgsz=imgsz,
            batch=batch_size,
            device=device,
            patience=50,  # 早停机制
            save=True,    # 保存最佳模型
            plots=True    # 保存训练过程图
        )
        
    def predict(self, image_path, conf=0.25):
        """预测单张图片"""
        if self.model is None:
            raise ValueError("请先训练模型或加载预训练模型！")
            
        results = self.model.predict(
            source=image_path,
            conf=conf,
            # save=True
        )
        return results
    
    def load_model(self, weights_path):
        """加载已训练的模型"""
        self.model = YOLO(weights_path)
        
    # def predict_folder(self, test_folder, output_folder, conf=0.25):
    #     """预测整个文件夹的图片"""
    #     if self.model is None:
    #         raise ValueError("请先训练模型或加载预训练模型！")
            
    #     # 确保输出文件夹存在
    #     os.makedirs(output_folder, exist_ok=True)
        
    #     results = self.model.predict(
    #         source=test_folder,
    #         conf=conf,
    #         save=True,
    #         project=output_folder
    #     )
    #     return results
    
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
    train_path = r"D:\WD\Weed_Detection_final\Weed_Detection\train\images"  # 训练集图片文件夹路径
    val_path = r"D:\WD\Weed_Detection_final\Weed_Detection\val\images"      # 验证集图片文件夹路径
    test_path = r"D:\WD\Weed_Detection_final\Weed_Detection\test\images"    # 测试集图片文件夹路径
    
    # 初始化检测器
    detector = GrowingPointDetector()
    
    # 准备数据配置文件
    detector.prepare_data_yaml(
        train_path=train_path,
        val_path=val_path,
        test_path=test_path,
        names=['weed', 'crop']  # 类别名称
    )
    
    # 训练模型
    detector.train(
        epochs=60,
        imgsz=640,
        batch_size=8,
        device='cpu'  # 改为使用 gPU 训练
    )
    
    # 预测测试集并保存结果到CSV
    stats = detector.evaluate_and_save(
        val_folder=test_path,  # 使用测试集路径
        output_csv='detection_results.csv',  # 指定CSV文件名
        conf=0.25
    )
    print("检测统计信息:", stats)
    
    # 如果还需要保存预测图片，可以继续使用predict_folder
    # detector.predict_folder(
    #     test_folder=test_path,
    #     output_folder='predictions',
    #     conf=0.25
    # )

if __name__ == "__main__":
    main()
