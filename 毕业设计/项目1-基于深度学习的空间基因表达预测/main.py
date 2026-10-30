"""Research prototype API. Missing models return 503; no synthetic predictions."""
from functools import lru_cache
import io
import time
from pathlib import Path
from fastapi import FastAPI, File, UploadFile, Form, HTTPException
from fastapi.responses import HTMLResponse
from PIL import Image, UnidentifiedImageError
from model_wrapper import GenePredictor, ModelUnavailable

app = FastAPI(title='空间基因表达预测 · 科研原型')
MAX_UPLOAD = 10 * 1024 * 1024

@lru_cache(maxsize=1)
def get_predictor(): return GenePredictor()

@app.get('/', response_class=HTMLResponse)
def root(): return (Path(__file__).parent/'index.html').read_text(encoding='utf-8')

@app.get('/health')
def health():
    try:
        get_predictor()
        return {'status':'ready','model_ready':True,'research_only':True}
    except ModelUnavailable:
        return {'status':'model_unavailable','model_ready':False,'research_only':True}

@app.post('/predict')
async def predict(image: UploadFile = File(...), genes: str = Form('EGFR,CD3D,CD68')):
    gene_list = [gene.strip() for gene in genes.split(',') if gene.strip()]
    if not gene_list or len(gene_list)>100 or len(set(gene_list))!=len(gene_list):
        raise HTTPException(400,'请提供 1–100 个不重复的基因名。')
    if any(len(gene)>80 or any(ord(c)<32 for c in gene) for gene in gene_list): raise HTTPException(400,'基因名格式无效。')
    contents=await image.read(MAX_UPLOAD+1)
    if len(contents)>MAX_UPLOAD: raise HTTPException(413,'图片超过 10 MB。')
    try:
        with Image.open(io.BytesIO(contents)) as decoded:
            if decoded.format not in {'PNG','JPEG'}: raise ValueError('PNG/JPEG only')
            if decoded.width*decoded.height>20_000_000: raise ValueError('Image is too large')
            decoded.load(); img=decoded.convert('RGB')
    except (UnidentifiedImageError, OSError, ValueError, Image.DecompressionBombError):
        raise HTTPException(400,'请上传有效的 PNG/JPEG 图片，最多 2000 万像素。')
    try: predictor=get_predictor()
    except ModelUnavailable as e: raise HTTPException(503,str(e))
    start=time.perf_counter()
    try: predictions=predictor.predict(img,gene_list)
    except (ValueError,KeyError): raise HTTPException(422,'后端输出与训练基因映射不一致，或数值无效。')
    return {'status':'success','predictions':predictions,'processing_time':round(time.perf_counter()-start,3),
            'research_only':True,'spatial_map_available':False}

if __name__=='__main__':
    import uvicorn
    uvicorn.run(app,host='127.0.0.1',port=8000)
