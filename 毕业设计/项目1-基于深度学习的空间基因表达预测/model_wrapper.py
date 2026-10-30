"""Strict integration boundary for a real, separately supplied research backend.

STFLOW_BACKEND must be 'python.module:factory'. The factory accepts no arguments
and returns an object with predict(PIL.Image, list[str]) -> dict[str, float].
The backend is responsible for the training gene mapping and preprocessing.
No model architecture, checkpoint dimensions or gene identities are guessed.
"""
import importlib
import math
import os

class ModelUnavailable(RuntimeError): pass

class GenePredictor:
    def __init__(self, backend=None):
        spec = backend or os.environ.get('STFLOW_BACKEND', '')
        if ':' not in spec: raise ModelUnavailable('模型未配置：缺少实际 STFlow 实现、训练权重和训练基因映射，请参阅 README。')
        module, factory = spec.rsplit(':', 1)
        try: self.backend = getattr(importlib.import_module(module), factory)()
        except Exception as e: raise ModelUnavailable('模型后端加载失败，请在本机检查配置、依赖和权重。') from e
        if not callable(getattr(self.backend, 'predict', None)): raise ModelUnavailable('后端缺少 predict(image, genes) 接口。')
    def predict(self, image, genes):
        result = self.backend.predict(image, genes)
        if not isinstance(result, dict) or set(result) != set(genes):
            raise ValueError('模型返回的基因与请求不一致；必须使用训练时的真实基因映射。')
        clean = {gene: float(result[gene]) for gene in genes}
        if not all(math.isfinite(value) for value in clean.values()): raise ValueError('模型返回非有限数值。')
        return clean
