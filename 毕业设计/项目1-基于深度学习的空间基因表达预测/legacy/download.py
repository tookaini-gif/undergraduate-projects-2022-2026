from huggingface_hub import snapshot_download

source_dataroot = "D:/STFlow-DKAN/dataset"
weights_root = "D:/STFlow-DKAN/dataset/weights_root"

# 下载数据集（关键！）
from huggingface_hub import snapshot_download

snapshot_download(
    repo_id="MahmoodLab/hest-bench",
    repo_type="dataset",
    local_dir="D:/STFlow-DKAN/dataset",
    allow_patterns=[
        "LUNG/*",
        "HCC/*"
    ]
)