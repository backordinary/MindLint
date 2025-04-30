from mindquantum.core.circuit import Circuit
from mindquantum.core.gates import H, X, Measure
from mindquantum.simulator import Simulator

# 构建 GHZ = (|000⟩+|111⟩)/√2
ghz = Circuit() \
      + H.on(0) \
      + X.on(1, 0) + X.on(2, 1) \
      + Measure('q0').on(0) + Measure('q1').on(1) + Measure('q2').on(2)

sim = Simulator('mqvector', ghz.n_qubits)
res = sim.sampling(ghz, shots=4096, seed=123)
print(ghz)
print(res)
