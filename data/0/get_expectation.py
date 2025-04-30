from mindquantum.core.circuit import Circuit
from mindquantum.core.gates import H, RY, RX
from mindquantum.simulator import Simulator
from mindquantum.core.operators import QubitOperator, Hamiltonian
from mindquantum.core.parameterresolver import ParameterResolver

circ = Circuit()
circ += H.on(0)  # 请补充代码
circ += RX('p0').on(1)
circ += RY('p1').on(1,0)
ham = Hamiltonian(
    QubitOperator('X0 Y1') + QubitOperator('Z0 Z1')
)

pr = ParameterResolver({'p0':0.1, 'p1':0.2})

sim = Simulator("mqvector", 2)
expectation = sim.get_expectation(ham, circ, pr=pr)  # 请补充代码

print(expectation)