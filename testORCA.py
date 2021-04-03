import matplotlib.pyplot as plt

plt.rcParams['font.sans-serif'] = ['KaiTi']  # 指定默认字体
# plt.rcParams['font.sans-serif'] = ['SongTi'] # 指定默认字体
plt.rcParams['axes.unicode_minus'] = False

x = []
for i in range(1, 16, 1):
    x.append(100 * i)

y, z = [], []
y0, z0 = 74.56, 23.16

# for i in range(len(x)):
#     y.append(74.56 / 99 * x[i])
#     z.append(23.16 / 99 * x[i])
fig, ax1 = plt.subplots()
ax2 = ax1.twinx()  # 做镜像处理

print(y)
print(z)
y = [75.31, 90.42, 105.23, 131.22, 161.01, 186.22, 200.02, 230.66, 264.55, 290.11, 299.56, 308.66, 310.22, 302.11,
     300.56]
z = [23.393, 29.23, 38.15, 45.96, 53.15, 61.56, 73.64, 82.30, 89.23, 99.2, 110.6, 124.8, 136, 149.6,
     172.12]

a = ax1.plot(x, y, 'g-s', label="疏散时间")
b = ax2.plot(x, z, 'r-^', label="伤亡人数")

ax1.set_xlabel('疏散行人总数(人)')  # 设置x轴标题
ax1.set_ylabel("总体疏散时间(秒)", color='black')  # 设置Y1轴标题
ax2.set_ylabel('伤亡人数(人)', color='black')
# ax2.ylim(0, 200)
ax2.plot([0], [221], color="w")
ax1.plot([0], [350], color="w")
ax1.legend(loc="upper left")
ax2.legend(loc="upper right")
plt.show()
