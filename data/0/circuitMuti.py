import numpy as np
from mindquantum import Circuit, RX, RY, Hamiltonian, X
from scipy.optimize import minimize
import numpy as np
from mindquantum import Simulator, Circuit, RY, Hamiltonian
from mindquantum.core.operators import QubitOperator
# 构建参数化电路
vqe_circ = Circuit()
vqe_circ += RX('theta1').on(0)
vqe_circ += RY('theta2').on(1)
vqe_circ += X.on(1, 0)  # 纠缠门

# 定义哈密顿量
ham = Hamiltonian(QubitOperator('Z0') + QubitOperator('X1'))

# 梯度优化
sim = Simulator('mqvector', 2)
grad_ops = sim.get_expectation_with_grad(ham, vqe_circ)

def cost_func(x):
    f, g = grad_ops(x)
    return f.real, g.real

# 使用BFGS优化
init_params = np.random.rand(2)
res = minimize(cost_func, init_params, method='BFGS', jac=True)
print(f"优化结果：\n最小值: {res.fun:.4f}\n最优参数: {res.x}")