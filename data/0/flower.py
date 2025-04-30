from mindquantum.core.circuit import shift, add_prefix, Circuit, UN
from mindquantum.core.gates import RZ, X, H

template = Circuit([X.on(1, 0), RZ('alpha').on(1), X.on(1, 0)])
encoder = UN(H, 4) + (RZ(f'{i}_alpha').on(i) for i in range(4)) + sum(add_prefix(shift(template, i), f'{i+4}') for i in range(3))
encoder.summary()
