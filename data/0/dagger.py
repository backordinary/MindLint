from mindquantum.core.circuit import dagger, Circuit
from mindquantum.core.gates import H, S, T, X

# 请补充如下代码片段：构造原始线路
circ = Circuit()
circ += H.on(0)
circ += T.on(1,0)
circ += S.on(1)
circ += X.on(2,1)

# 请补充如下代码片段
dag_circ = dagger(circ)

dag_circ.svg()