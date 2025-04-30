from mindquantum.core.gates import H, RY, X
from mindquantum.core.circuit import Circuit, UN
from mindquantum.core.operators import Hamiltonian, QubitOperator
from mindquantum.simulator import Simulator
from scipy.optimize import minimize
import numpy as np

# 请补充如下代码片段
circ = Circuit()
for i in range(4):
    circ += H.on(i)
    circ += RY(f"p{i}").on(i)
for i in range(3):
    circ += X.on(i+1,i)
for i in range(4):
    circ += RY(f"p{4+i}").on(i)

# 请补充如下代码片段
ham = Hamiltonian(
    QubitOperator("Z0 Z1") + QubitOperator("Z1 Z3")
)

# 请补充如下代码片段
sim = Simulator("mqvector", 4)
grad_ops = sim.get_expectation_with_grad(
    ham,
    circ
)

def fun(x):
    f, g = grad_ops(x)
    return f.squeeze().real, g.squeeze().real

res = minimize(fun, np.ones(len(circ.params_name)), method="BFGS", jac=True)
min_value = res.fun
print(min_value)