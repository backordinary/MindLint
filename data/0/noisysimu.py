from mindquantum import *
import numpy as np
# 克隆基础电路
base_circ = Circuit([H.on(0), RX(np.pi/2).on(1), X.on(1, 0)])

# 添加振幅阻尼噪声
noisy_circ = base_circ.copy()
noisy_circ += AmplitudeDampingChannel(0.1).on(0)
noisy_circ += AmplitudeDampingChannel(0.1).on(1)

# 对比模拟结果
sim = Simulator('mqvector', 2)
ham = Hamiltonian(QubitOperator('Z0 Z1'))

# 无噪声
exp_clean = sim.get_expectation(ham, base_circ)
# 有噪声
exp_noise = sim.get_expectation(ham, noisy_circ)

print(f"期望值对比：\n无噪声: {exp_clean.real:.4f}\n含噪声: {exp_noise.real:.4f}")