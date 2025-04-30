from mindquantum.core.circuit import apply, Circuit, controlled
from mindquantum.core.gates import H, Y, Z, SWAP

# 原始线路
circ = Circuit()
circ += Y.on(0)
circ += SWAP.on([1, 0])
circ += Z.on(1)

# 请补充如下代码片段：将circ作用在比特q2, q3上
temp_circ = apply(circ,[2,3])

new_circ = Circuit()
new_circ += H.on(0)
new_circ += H.on(1)
new_circ += controlled(temp_circ)([0, 1])

new_circ.svg()