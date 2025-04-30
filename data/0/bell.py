from mindquantum import *

# 构建贝尔态电路
bell_circ = Circuit()
bell_circ += H.on(0)
bell_circ += X.on(1, 0)  # CNOT门
bell_circ += Measure('q0').on(0)
bell_circ += Measure('q1').on(1)

# 模拟采样
sim = Simulator('mqvector', 2)
res = sim.sampling(bell_circ, shots=1000)
print("贝尔态采样结果：")
print(res)

# 计算期望值
ham = Hamiltonian(QubitOperator('X0 X1') - QubitOperator('Y0 Y1'))
exp = sim.get_expectation(ham, bell_circ)
print(f"\n期望值: {exp.real:.4f}")