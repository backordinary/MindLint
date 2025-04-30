from mindquantum import Circuit, H, X, Z, RX, RY, RZ, CNOT, SWAP

# **📌 创建一个量子线路**
qc = Circuit()

# **✅ 单量子比特门**
qc += H.on(0)  # 在量子比特 0 上添加 Hadamard 门
qc += RX(1.57).on(1)  # 在量子比特 1 上添加 RX 门（参数为 1.57 弧度）
qc += RY(0.5).on(1)  # 在量子比特 2 上添加 RY 门（参数为 0.5 弧度）

# **✅ 双量子比特门**
qc += CNOT.on(0, 1)  # 在量子比特 0 和 1 上添加 CNOT 门（控制量子比特 0，目标量子比特 1）

qc += X.on(0,1,2)
# **✅ 打印量子线路**
print("量子线路：")
print(qc)

# **✅ 运行量子线路**
from mindquantum.simulator import Simulator

# 使用 Simulator 运行线路
sim = Simulator('mqvector', 2)  # 使用 mqvector 后端，3 个量子比特
result = sim.sampling(qc, shots=1000)  # 运行线路 1000 次

# **✅ 输出结果**
print("\n测量结果：")
print(result)