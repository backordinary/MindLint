from mindquantum import Circuit, Simulator
from mindquantum.core.gates import X, CNOT, Measure

# 初始化线路
circuit = Circuit()

# 正常使用
circuit += X.on(0,[1,2])
circuit += Measure('m0').on(1)
circuit += Measure('m1').on([0,1])
# 错误用法：被测量的 qubit(0) 被作为控制位再次使用
circuit += CNOT.on(0, 1)  # ❌ 错误！1 已被测量
# 使用 Simulator 运行线路
sim = Simulator('mqvector', 3)  # 使用 mqvector 后端，3 个量子比特
result = sim.sampling(circuit, shots=1000)  # 运行线路 1000 次
print(circuit)
print(result)