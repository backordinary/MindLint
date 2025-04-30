import numpy as np                                          # 导入numpy库并简写为np
from mindquantum.core.gates import X, Y, Z, H, RX, RY, RZ   # 导入量子门H, X, Y, Z, RX, RY, RZ
from mindquantum.core.circuit import Circuit     # 导入Circuit模块，用于搭建量子线路

encoder = Circuit()                              # 初始化量子线路
encoder += H.on(0)                               # H门作用在第0位量子比特
encoder += X.on(1, 0)                            # X门作用在第1位量子比特且受第0位量子比特控制
encoder += RY('theta').on(2)                     # RY(theta)门作用在第2位量子比特

print(encoder)                                   # 打印Encoder
encoder.summary()                                # 总结Encoder量子线路
encoder.svg()
