from mindquantum import *
import numpy as np

# 1. 创建量子电路并添加参数化门
n_qubits = 2
circ = Circuit()
alpha = ParameterResolver('a')  # 定义参数解析器
circ += RX(alpha).on(0)         # 在0号量子位添加RX门，参数为alpha
circ += H.on(1)                 # 在1号量子位添加Hadamard门
circ += X.on(1, 0)              # 添加CNOT门（控制位0，目标位1）

# 2. 添加测量门并显示电路
circ += Measure('q0').on(0)
circ += Measure('q1').on(1)
print("量子电路：")
print(circ)

# 3. 构建哈密顿量
ham = Hamiltonian(QubitOperator('Z0 Z1'))  # 使用泡利Z算符构造哈密顿量

# 4. 使用无噪声模拟器计算期望值
sim = Simulator('mqvector', n_qubits)
params = {'a': np.pi/2}  # 设置参数值
exp = sim.get_expectation(ham, circ, params)
print(f"\n期望值（无噪声）: {exp.real}")

# 5. 添加去极化噪声并重新模拟
noisy_circ = circ.clone()  # 克隆原始电路
depolar = DepolarizingChannel(0.1)  # 创建去极化信道（错误率10%）
noisy_circ += depolar.on(0)         # 在0号量子位添加噪声

noisy_sim = Simulator('mqvector', n_qubits)
noisy_exp = noisy_sim.get_expectation(ham, noisy_circ, params)
print(f"期望值（带噪声）: {noisy_exp.real}")

# 6. 带梯度计算的参数优化
sim.reset()  # 重置模拟器状态
grad_ops = sim.get_expectation_with_grad(ham, circ)

def optimize(init_param, lr=0.1, steps=50):
    param = init_param
    for _ in range(steps):
        exp, grad = grad_ops(param)
        param -= lr * grad[0].real  # 梯度下降
    return param

final_param = optimize(np.array([0.5]))  # 初始参数0.5
print(f"\n优化后参数: {final_param[0]:.4f}")

# 7. 量子采样示例
sampling_result = sim.sampling(circ, params, shots=1000)
print("\n采样结果：")
print(sampling_result)