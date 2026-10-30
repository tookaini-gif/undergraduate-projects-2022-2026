import h5py

f = h5py.File(r"D:/STFlow-DKAN/dataset/embed_dataroot/LUNG/resnet50_trunc/fp32/TENX118.h5", 'r')
print(list(f.keys()))
f.close()