import numpy as np
import matplotlib.pyplot as plt
from mindquantum import Simulator, Circuit, H, X, Z, Measure

# 1. 构建 Grover 电路（2 比特，查找目标态 |11>）
circ = Circuit()
# 初始化所有比特为 |+> 态
circ += H.on(0)
circ += H.on(1)
# Oracle 子电路：对 |11> 态施加相位翻转（使用受控Z门，以0号比特控制1号比特）
circ += Z.on(1, 0)   # 当 q0=1 且 q1=1 时，在q1施加Z相位（仅 |11> 态获得相位 -1）
# 扩散子电路：相当于对 |00> 态（均匀态的反射点）施加相位翻转
circ += H.on(0)
circ += H.on(1)
circ += X.on(0)
circ += X.on(1)
circ += Z.on(1, 0)   # （经过X后，|00> 态变为 |11>，再次对其施加受控相位翻转）
circ += X.on(0)
circ += X.on(1)
circ += H.on(0)
circ += H.on(1)
# 添加测量
circ += Measure('q0').on(0)
circ += Measure('q1').on(1)

# 2. 初始化模拟器并执行电路多次采样
sim = Simulator('mqvector', circ.n_qubits)
res = sim.sampling(circ, shots=100)  # 采样100次
counts = dict(res)
print("Sampling counts:", counts)

# 3. 绘制测量结果分布
bitstrings = ['00','01','10','11']
probs = [(counts.get(s, 0) / 100) for s in bitstrings]  # 各状态频率
plt.figure()
plt.bar(bitstrings, probs, color='coral')
plt.xlabel("Bitstring")
plt.ylabel("Probability")
plt.title("Grover search output")
for s, p in zip(bitstrings, probs):
    plt.text(s, p+0.02, f"{p*100:.0f}%", ha='center')
plt.show()
