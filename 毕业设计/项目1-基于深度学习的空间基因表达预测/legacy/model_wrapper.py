# model_wrapper.py
import torch
from PIL import Image
from torchvision import transforms
import numpy as np
import io
import matplotlib.pyplot as plt
import base64
from stflow.flow.model import STFlowDKAN  # 替换成你的模型定义文件路径

class GenePredictor:
    def __init__(self, model_path="D:/STFlow-DKAN/runs/test/LUNG_TENX118/best_model.pt", device="cpu"):
        self.device = torch.device(device)
        print(f"✅ Loading trained model from {model_path} on {self.device}")

        # 初始化模型（参数按训练时一致）
        self.model = STFlowDKAN(img_channels=1, expr_dim=50, out_dim=50)
        ckpt = torch.load(model_path, map_location=self.device)
        self.model.load_state_dict(ckpt["model"])
        self.model.to(self.device)
        self.model.eval()

        # 图像预处理
        self.transform = transforms.Compose([
            transforms.Grayscale(),           # 保证单通道
            transforms.Resize((256, 256)),   # 训练尺寸
            transforms.ToTensor()
        ])

    def predict(self, img: Image.Image, genes: list):
        """
        输入:
            img: PIL.Image
            genes: list[str]
        输出:
            dict {gene_name: float}
        """
        # 图像预处理
        x = self.transform(img).unsqueeze(0).to(self.device)  # (1,C,H,W)

        # 构造 dummy expr 输入 (模型训练时需要)
        expr_dummy = torch.zeros((1, len(genes), 1), device=self.device)  # 简化处理

        # 模型预测
        with torch.no_grad():
            out = self.model(x, expr_dummy)  # (B, n_genes, dim) 或 (B, n_genes)
            out = out.squeeze(0).cpu().numpy()[:len(genes)]

        # 归一化到0~10
        out = (out - out.min()) / (out.max() - out.min() + 1e-8) * 10

        # 返回字典
        predictions = {genes[i]: float(out[i]) for i in range(len(genes))}
        return predictions

    def generate_heatmap(self, img: Image.Image, gene_value: float):
        """
        根据预测值生成叠加热图 (返回base64)
        """
        img_resized = img.resize((100, 100))
        heatmap_arr = np.random.rand(100, 100) * gene_value

        fig, ax = plt.subplots(figsize=(6,6))
        ax.imshow(img_resized)
        im = ax.imshow(heatmap_arr, cmap='hot', alpha=0.5)
        ax.axis('off')
        plt.colorbar(im, fraction=0.046, pad=0.04)
        plt.tight_layout()

        buf = io.BytesIO()
        plt.savefig(buf, format='png')
        buf.seek(0)
        heatmap_base64 = base64.b64encode(buf.read()).decode('utf-8')
        plt.close(fig)

        return heatmap_base64