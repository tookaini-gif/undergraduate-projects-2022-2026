import argparse
from pathlib import Path

def main():
    p=argparse.ArgumentParser(description='Inspect the top-level keys of a local HDF5 file')
    p.add_argument('file',type=Path); a=p.parse_args()
    if not a.file.is_file(): p.error('file does not exist')
    import h5py
    with h5py.File(a.file,'r') as handle: print(list(handle.keys()))
if __name__=='__main__': main()
