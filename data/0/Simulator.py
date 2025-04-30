from mindquantum.core.circuit import Circuit
from mindquantum.simulator import Simulator

# 定义一个简单的量子线路
circuit = Circuit().h(0)  # 对第0个量子比特应用Hadamard门

# 初始化模拟器
sim = Simulator('mqvector', 2)  # 使用'mqvector'后端

# 在模拟器上应用量子线路
sim.apply_circuit(circuit)

# 获取并打印量子态
quantum_state = sim.get_qs()
print("Quantum State:", quantum_state)
