import random
import math
import matplotlib.pyplot as plt

plt.rcParams['font.sans-serif'] = ['KaiTi']  # 指定默认字体
# plt.rcParams['font.sans-serif'] = ['宋体'] # 指定默认字体
plt.rcParams['axes.unicode_minus'] = False


# 74.56 * 100 = 7456


def get_gauss(n, miu, sigma, up, low=0):
    time = []
    for i in range(n):
        d = random.gauss(miu, sigma)
        while d <= low or d > up:
            d = random.gauss(miu, sigma)
        time.append(d)
    return time


def get_normal_scene():
    time = []
    seed = [[5, 14, 2.3], [17, 17, 3.4], [31, 24, 4.5], [48, 15, 4.5], [59, 10, 5.8]]
    for seq in seed:
        time += get_gauss(seq[1], seq[0], seq[2], 74.56, 1)
    draw_pic(time, 74.56)


def draw_pic(seq, limit):
    step = 5
    start = 1
    x, y = [], []
    su = 0
    for d in seq:
        su += d

    print(su / len(seq))

    while start + step <= limit:
        cnt = 0
        for data in seq:
            if start <= data < start + step:
                cnt += 1
        x.append(start)
        y.append(cnt)
        start += step
    fig = plt.figure(1)
    ax = fig.add_subplot(111)
    plt.bar(x, y, width=4.0, color="sandybrown")
    plt.title('优化后行人疏散时间分布')
    plt.xlabel("疏散时间")
    plt.ylim(0, 15)
    plt.ylabel("个数")
    # plt.savefig("普通疏散分布.png")
    plt.show()


if __name__ == '__main__':
    get_normal_scene()
