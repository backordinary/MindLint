import numpy as np, matplotlib.pyplot as plt
from mindquantum import Circuit, H, X, RZ, RX, Measure, Simulator
from mindquantum.core.parameterresolver import ParameterResolver

# ── 构建单层 QAOA 电路 ──────────────────────────────────────
qaoa = Circuit()

# 1) |+> 初始化（逐比特加 Hadamard）
for q in [0, 1]:
    qaoa += H.on(q)

# 2) 成本哈密顿量 e^{-iγ Z0Z1}
qaoa += X.on(1, 0)
qaoa += RZ('2γ').on(1)   # γ 以符号形式写入
qaoa += X.on(1, 0)

# 3) 混合哈密顿量 e^{-iβ (X0+X1)}
for q in [0, 1]:
    qaoa += RX('2β').on(q)

# 4) 测量
qaoa += Measure('q0').on(0)
qaoa += Measure('q1').on(1)

# ── 绑定参数（ParameterResolver） ───────────────────────────
pr = ParameterResolver({'β': 0.6, 'γ': 0.8})

# ── 采样并读取 MeasureResult.data ─────────────────────────
sim = Simulator('mqvector', qaoa.n_qubits)
res = sim.sampling(qaoa, pr=pr, shots=1000, seed=42)

counts = res.data                     # 计数字典
probs  = {k: v / res.shots for k, v in counts.items()}

# ── 绘制输出概率分布 ────────────────────────────────────────
plt.bar(probs.keys(), probs.values())
plt.title("QAOA distribution")
plt.xlabel("Bitstring (little-endian)")
plt.ylabel("Probability")
plt.show()
