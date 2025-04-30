#pylint: disable=W0611
import numpy as np
from fractions import Fraction
import mindquantum as mq
from mindquantum.core.gates import X, Z, H, UnivMathGate, Measure
from mindquantum.core.circuit import Circuit, controlled, UN
from mindquantum.algorithm.library import qft
from mindquantum.simulator import Simulator
def U_operator(N, a, register1, register2):
    Q = 2**len(register1)
    x = []
    f = []
    for i in range(Q):
        x.append(i)
        f.append(a**i % N)  # 计算f(x)

    # 创建量子态|register2>的矩阵表示
    vector = np.zeros((Q, Q))
    for i in range(Q):
        vector[i, i] = 1

    T = []
    for i in range(Q):
        matrix = np.outer(vector[f[i]], vector[0])  # 计算映射Tx的矩阵
        T.append(UnivMathGate(f'f({i})', matrix))  # 用变换矩阵构造Tx“门”

    # 创建控制线路，得到算子U。对于每个Tx“门”，都受寄存器1中所有比特控制，其对应x的二进制中比特位是1的是正常控制节点，比特位是0的则要在控制节点两侧作用X门，翻转控制位
    circuit = Circuit()
    for i in range(Q):
        bin_x = bin(x[i])[2:]  # 将x转换为二进制
        flip_control_qubit = list(range(len(register1)))  # 初始化需要作用X门的比特的list

        for j in range(len(bin_x)):
            if bin_x[len(bin_x) - j - 1] == '1':  # 获得x的二进制中是‘1’的比特
                flip_control_qubit.remove(j)  # 从list中删除不需要作用X门的控制比特

        circuit.barrier()  # 添加barrier
        circuit += UN(X, flip_control_qubit)  # 在控制节点前作用X门
        circuit += T[x[i]].on(register2, list(register1))  # 给Tx“门”接上控制比特
        circuit += UN(X, flip_control_qubit)  # 在控制节点后作用X门

    return circuit

q = 4  # 比特数
N = 15
a = 2
x = []
f = []
for i in range(2**q):
    x.append(i)
    f.append(a**i % N)

register1 = range(4)
register2 = range(4, 8)
circuit = Circuit(X.on(2))  # 创建线路，使输入态为|0100⟩|0000⟩，即x=8，|8⟩|0⟩
circuit += U_operator(15, 2, register1, register2)  # 作用U算子

print(circuit.get_qs('mqvector', ket=True))  # 打印末态
circuit.svg() #打印线路

