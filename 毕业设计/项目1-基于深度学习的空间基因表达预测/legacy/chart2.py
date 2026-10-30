import matplotlib.pyplot as plt
import numpy as np

# 数据
datasets = ['LUNG-TENX118', 'HCC-NCBI642', 'HCC-NCBI643']
pearson = [0.236, 0.099, 0.092]
r2 = [-0.624, -0.064, -0.044]
l2 = [5.0, 0.3, 0.3]  # 近似平均值

x = np.arange(len(datasets))
width = 0.25

fig, ax1 = plt.subplots(figsize=(10,6))

# 绘制 Pearson 和 R2
ax1.bar(x - width, pearson, width, label='Pearson', color='skyblue')
ax1.bar(x, r2, width, label='R²', color='salmon')
ax1.set_ylabel('Pearson / R²')
ax1.set_ylim(-1, 1)
ax1.axhline(0.3, color='green', linestyle='--', label='理想 Pearson >0.3')
ax1.axhline(0.0, color='gray', linestyle='--', label='R²参考线')
ax1.set_xticks(x)
ax1.set_xticklabels(datasets)
ax1.set_title('模型预测指标比较')

# 绘制 L2（次坐标轴）
ax2 = ax1.twinx()
ax2.bar(x + width, l2, width, label='L2', color='gold')
ax2.set_ylabel('L2误差')
ax2.set_ylim(0, max(l2)*1.2)

# 图例合并
handles1, labels1 = ax1.get_legend_handles_labels()
handles2, labels2 = ax2.get_legend_handles_labels()
ax1.legend(handles1 + handles2, labels1 + labels2, loc='upper right')

plt.tight_layout()
plt.show()