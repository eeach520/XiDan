import random
import math
import matplotlib.pyplot as plt

x, y = [], []
prev = 0


def fun1(i):
    return 2653 - 2653 / 99999 * i


def fun2(i):
    return 2653 / (math.sqrt(math.sqrt(math.sqrt(i)))) - 500.0


def get_d(i, t):
    return t / 10


for i in range(1, 100000, 100):
    x.append(i)

    t = random.uniform(0, 20)
    tt = random.random() * 0.3

    mis = fun2(i) * (1 - tt) + fun1(i) * tt
    if mis > 2653:
        mis = random.uniform(2000, 3000)
    d = mis
    delta = 500 - 500 / 99999 * i
    d += random.uniform(delta * -1, delta)
    y.append(d)
plt.figure()
plt.plot(x, y)
plt.xlabel("epoch")
plt.ylabel("loss")
plt.show()

print(fun2(99999))

for i in range(100):
    print(random.random())
