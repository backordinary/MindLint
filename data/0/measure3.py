from mindquantum import Simulator
from mindquantum.core.circuit import Circuit

circuit = Circuit().h(0).x(1, 0).measure_all()

# 错误：再次用测量过的 qubit 0 作为控制位
circuit.x(2, 0)
print(circuit)
sim = Simulator('mqvector', 3)  # 使用 mqvector 后端，3 个量子比特
result = sim.sampling(circuit, shots=1000)  # 运行线路 1000 次
print(result)