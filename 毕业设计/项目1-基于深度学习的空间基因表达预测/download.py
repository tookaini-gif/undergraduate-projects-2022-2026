import argparse
from pathlib import Path

def main():
    p=argparse.ArgumentParser(description='Download authorized HEST benchmark subsets; dataset terms and access apply')
    p.add_argument('--output',type=Path,required=True)
    a=p.parse_args()
    from huggingface_hub import snapshot_download
    snapshot_download(repo_id='MahmoodLab/hest-bench',repo_type='dataset',local_dir=str(a.output),allow_patterns=['LUNG/*','HCC/*'])
if __name__=='__main__': main()
