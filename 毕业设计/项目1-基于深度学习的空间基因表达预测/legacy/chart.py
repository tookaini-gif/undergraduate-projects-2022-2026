import matplotlib.pyplot as plt
import seaborn as sns
import numpy as np

# 数据（根据你训练输出整理）
datasets = ['LUNG-TENX118', 'HCC-NCBI642', 'HCC-NCBI643']

# Pearson 平均值
pearson_means = [0.2359, 0.0992, 0.0920]

# R² 平均值
r2_means = [-0.624, -0.064, -0.044]  # 这里用各自r2_score_q1/q2/q3平均值近似

# L2 平均值
l2_means = [np.mean([5.512,2.826,0.281,15.405,1.347,0.957]),  # 只用前6个做示例，可替换成全部
            np.mean([0.214,0.421,0.400,0.180,0.121,0.173]),
            np.mean([0.222,0.517,0.820,0.289,0.259,0.245])]

x = np.arange(len(datasets))  # X轴位置
width = 0.25  # 柱子宽度

fig, ax1 = plt.subplots(figsize=(10,6))

# 绘制 Pearson
rects1 = ax1.bar(x - width, pearson_means, width, label='Pearson', color='skyblue')

# 绘制 R²
rects2 = ax1.bar(x, r2_means, width, label='R²', color='salmon')

# 绘制 L2
rects3 = ax1.bar(x + width, l2_means, width, label='L2', color='lightgreen')

ax1.set_ylabel('指标值')
ax1.set_xticks(x)
ax1.set_xticklabels(datasets)
ax1.set_title('三个数据集的 Pearson、R² 和 L2 指标对比')
ax1.legend()

# 添加数值标签
def add_labels(rects):
    for rect in rects:
        height = rect.get_height()
        ax1.annotate(f'{height:.2f}',
                     xy=(rect.get_x() + rect.get_width() / 2, height),
                     xytext=(0, 3),  # 垂直偏移
                     textcoords="offset points",
                     ha='center', va='bottom')

add_labels(rects1)
add_labels(rects2)
add_labels(rects3)

plt.tight_layout()
plt.show()