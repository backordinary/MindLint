import matplotlib.pyplot as plt
from mindquantum import *
# 定义海森堡模型哈密顿量
ham = QubitOperator('X0 X1') + QubitOperator('Y0 Y1') + QubitOperator('Z0 Z1')



# 参数设置
times = np.linspace(0, 2*np.pi, 50)
expectations = []

# 模拟演化过程
sim = Simulator('mqvector', 2)
for t in times:
    # 生成时间演化电路
    time_evo = TimeEvolution(ham, t).circuit
    exp = sim.get_expectation(Hamiltonian(ham), time_evo)
    expectations.append(exp.real)

# 可视化结果
plt.plot(times, expectations)
plt.xlabel('Time')
plt.ylabel('Expectation Value')
plt.title('Time Evolution Simulation')
plt.show()