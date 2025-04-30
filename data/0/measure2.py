from mindquantum import Simulator
from mindquantum.core.circuit import Circuit

# 构建一个简单量子线路
circuit = Circuit().h(0).x(1, [2,0]).measure(0)

# 错误使用：测量后仍将 qubit 0 用作控制位
circuit.x(2, [0,1])
print(circuit)
sim = Simulator('mqvector', 3)  # 使用 mqvector 后端，3 个量子比特
result = sim.sampling(circuit, shots=1000)  # 运行线路 1000 次
print(result)
