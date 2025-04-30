from mindquantum import *
from mindquantum import Circuit, RY, X
# 构建多控制门电路
complex_circ = Circuit()
# 在0号量子位添加H门
complex_circ += H.on(0)
# 并行RY门
complex_circ += UN(RY, [1,2,3], 'theta')  # theta为参数前缀
# 交换门组合
complex_circ += SWAP.on([1,2])  # 交换1和2号量子位
complex_circ += X.on(3, [0,1,2], [1,1,1])  # 多控制非门

# 可视化电路
complex_circ.svg().to_file('complex_circuit.svg')
print("复杂电路结构已保存为SVG文件")