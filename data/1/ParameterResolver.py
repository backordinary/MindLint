from mindquantum.core.gates import H, RX, X
from mindquantum.core.parameterresolver import ParameterResolver
from mindquantum.core.circuit import Circuit
from mindquantum.simulator import Simulator
import numpy as np

# 请补充如下代码片段
circ = Circuit()
circ += H.on(0)
circ += X.on(1)
circ += RX('p0').on(0)
circ += RX('p1').on(1)

# 请补充如下代码片段
pr = ParameterResolver({'p0': np.pi,'p1': -np.pi})

sim = Simulator("mqvector", 2)
sim.apply_circuit(circ, pr=pr)

final_state = sim.get_qs(ket=True)
print(final_state)