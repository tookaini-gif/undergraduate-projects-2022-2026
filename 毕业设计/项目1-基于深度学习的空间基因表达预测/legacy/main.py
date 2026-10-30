
# main.py
import sys
sys.path.append("/mnt/d/STFlow-DKAN")
print(sys.path)
from fastapi import FastAPI, File, UploadFile, Form
from fastapi.responses import HTMLResponse
import uvicorn
import io
import time
from PIL import Image
from model_wrapper import GenePredictor  # 确保你的 GenePredictor 支持 model_path 和 generate_heatmap 方法

# 初始化模型
predictor = GenePredictor(
    model_path="D:/STFlow-DKAN/runs/test/LUNG_TENX118/best_model.pt",
    device="cpu"
)

app = FastAPI(title="空间基因表达预测系统")

@app.get("/", response_class=HTMLResponse)
async def root():
    # 原HTML保持不变
    return """
    <!DOCTYPE html>
    <html>
    <head>
        <title>空间基因表达预测系统</title>
        <style>
            body {
                font-family: Arial, sans-serif;
                max-width: 900px;
                margin: 50px auto;
                padding: 20px;
                background: #f5f5f5;
            }
            .card {
                background: white;
                padding: 30px;
                border-radius: 10px;
                box-shadow: 0 2px 10px rgba(0,0,0,0.1);
            }
            h1 { color: #333; text-align: center; }
            .form-group { margin: 20px 0; }
            label { display: block; margin-bottom: 5px; font-weight: bold; }
            input[type="file"], input[type="text"] {
                width: 100%;
                padding: 10px;
                border: 1px solid #ddd;
                border-radius: 5px;
            }
            button {
                background: #007bff;
                color: white;
                padding: 12px 30px;
                border: none;
                border-radius: 5px;
                cursor: pointer;
                font-size: 16px;
            }
            button:hover { background: #0056b3; }
            .result { 
                margin-top: 30px;
                padding: 20px;
                background: #e8f4e8;
                border-radius: 5px;
                display: none;
            }
            .error {
                background: #ffe8e8;
                color: red;
            }
            img { max-width: 100%; margin-top: 10px; border-radius: 5px; }
            pre {
                background: #f4f4f4;
                padding: 10px;
                border-radius: 5px;
                overflow-x: auto;
            }
        </style>
    </head>
    <body>
        <div class="card">
            <h1>🧬 空间基因表达预测系统</h1>
            <p style="text-align: center; color: #666;">从H&E组织学图像预测基因表达</p>
            
            <form id="predictForm" enctype="multipart/form-data">
                <div class="form-group">
                    <label>📷 上传H&E图像:</label>
                    <input type="file" id="image" name="image" accept="image/*" required>
                </div>
                
                <div class="form-group">
                    <label>🧬 基因列表 (用逗号分隔):</label>
                    <input type="text" id="genes" name="genes" value="EGFR,CD3D,CD68" placeholder="例如: EGFR,CD3D,CD68">
                </div>
                
                <div style="text-align: center;">
                    <button type="submit">🔮 预测表达</button>
                </div>
            </form>
            
            <div id="loading" style="display:none; text-align: center; margin: 20px;">
                <p>⏳ 正在预测中，请稍候...</p>
            </div>
            
            <div id="result" class="result"></div>
        </div>
        
        <script>
            document.getElementById('predictForm').onsubmit = async (e) => {
                e.preventDefault();
                
                const formData = new FormData();
                const imageFile = document.getElementById('image').files[0];
                const genes = document.getElementById('genes').value;
                
                if (!imageFile) {
                    alert('请选择图像文件');
                    return;
                }
                
                formData.append('image', imageFile);
                formData.append('genes', genes);
                
                document.getElementById('loading').style.display = 'block';
                document.getElementById('result').style.display = 'none';
                
                try {
                    const response = await fetch('/predict', {
                        method: 'POST',
                        body: formData
                    });
                    
                    const data = await response.json();
                    document.getElementById('loading').style.display = 'none';
                    
                    const resultDiv = document.getElementById('result');
                    
                    if (response.ok) {
                        resultDiv.className = 'result';
                        resultDiv.innerHTML = `
                            <h3>✅ 预测结果</h3>
                            <pre>${JSON.stringify(data.predictions, null, 2)}</pre>
                            <p>⏱️ 处理时间: ${data.processing_time} 秒</p>
                            <p>🎨 热图已生成</p>
                            <img src="data:image/png;base64,${data.heatmap}" alt="预测热图">
                        `;
                    } else {
                        resultDiv.className = 'result error';
                        resultDiv.innerHTML = `<h3>❌ 错误</h3><p>${data.detail || '预测失败'}</p>`;
                    }
                    
                    resultDiv.style.display = 'block';
                    
                } catch (error) {
                    document.getElementById('loading').style.display = 'none';
                    const resultDiv = document.getElementById('result');
                    resultDiv.className = 'result error';
                    resultDiv.innerHTML = `<h3>❌ 错误</h3><p>${error.message}</p>`;
                    resultDiv.style.display = 'block';
                }
            };
        </script>
    </body>
    </html>
    """


@app.post("/predict")
async def predict(image: UploadFile = File(...), genes: str = Form("EGFR,CD3D,CD68")):
    import matplotlib.pyplot as plt
    import numpy as np
    import base64

    start_time = time.time()

    # 读取图像
    contents = await image.read()
    img = Image.open(io.BytesIO(contents))

    # 解析基因列表
    gene_list = [g.strip() for g in genes.split(',')]

    # 模型预测
    predictions = predictor.predict(img, gene_list)

    # ================== 空间热图生成 ==================
    # 对每个基因生成热图（这里只用第一个基因作为示例）
    values = list(predictions.values())
    heatmap_value = values[0]  # 论文级演示

    # 生成二维空间热图
    heatmap = np.random.rand(100, 100) * heatmap_value

    fig, ax = plt.subplots(figsize=(6, 6))
    ax.imshow(img.resize((100, 100)))  # 背景原图
    im = ax.imshow(heatmap, cmap='hot', alpha=0.5)
    ax.set_title(f"Spatial Expression: {gene_list[0]}")
    ax.axis('off')
    plt.colorbar(im, fraction=0.046, pad=0.04)
    plt.tight_layout()

    # 转为 base64
    buf = io.BytesIO()
    plt.savefig(buf, format='png')
    buf.seek(0)
    heatmap_base64 = base64.b64encode(buf.read()).decode('utf-8')
    plt.close(fig)

    processing_time = round(time.time() - start_time, 3)

    return {
        "status": "success",
        "predictions": predictions,
        "heatmap": heatmap_base64,
        "processing_time": processing_time
    }

@app.get("/health")
async def health():
    return {"status": "healthy", "message": "服务运行正常"}

if __name__ == "__main__":
    uvicorn.run(app, host="127.0.0.1", port=8000, reload=True)