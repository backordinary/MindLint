import numpy as np
import matplotlib.pyplot as plt
from mindquantum import Simulator, Circuit, RY, Hamiltonian
from mindquantum.core.operators import QubitOperator

# 1. 构建含参数的量子电路（两比特系统，每个比特上一个参数化的RY旋转）
circ = Circuit()
circ += RY('a').on(0)   # 在0号量子比特上作用参数为 'a' 的RY旋转门
circ += RY('b').on(1)   # 在1号量子比特上作用参数为 'b' 的RY旋转门

# 绘制量子线路图（在Jupyter环境下会显示电路的SVG图像）
circ.svg()

# 2. 定义哈密顿量 H = Z0 + Z1 作为需要最小化期望值的观测量
H = Hamiltonian(QubitOperator('Z0') + QubitOperator('Z1'))

# 3. 初始化模拟器（选择"mqvector"后端）并获取计算期望值及梯度的算子
sim = Simulator('mqvector', circ.n_qubits)
grad_ops = sim.get_expectation_with_grad(H, circ)

# 4. 准备初始参数值，并设定优化步长等
np.random.seed(42)
theta = np.random.uniform(0, 2*np.pi, size=len(circ.params_name))  # 随机初始化参数 ['a','b']
learning_rate = 0.2
max_iters = 50

# 5. 优化循环：利用梯度下降迭代更新参数，记录每次的能量期望值
energy_history = []
for it in range(max_iters):
    # 计算当前参数下的期望值 f 和梯度 g
    f, g = grad_ops(theta)
    # MindQuantum返回的 f, g 为多维数组，需要取实部并降维
    f = np.real(f).ravel()[0]   # 期望值f是形状(1,1)的数组，取实部并展平成标量
    g = np.real(g)[0, 0]        # 梯度g是形状(1,1,2)的数组，这里取出(2,)的一维数组
    energy_history.append(f)
    # 输出迭代信息（每10步）
    if (it+1) % 10 == 0:
        print(f"Iteration {it+1}: E = {f:.4f}")
    # 用梯度下降法更新参数：theta_new = theta - η * ∇f
    theta -= learning_rate * g

# 6. 打印优化结束后的结果
final_energy = energy_history[-1]
print(f"Optimized energy ≈ {final_energy:.4f}, parameters = {theta}")

# 7. 绘制能量收敛曲线
plt.figure()
plt.plot(energy_history, marker='o', color='orange')
plt.title("Energy Convergence")
plt.xlabel("Iteration")
plt.ylabel("Energy expectation value")
plt.grid(True)
plt.show()
