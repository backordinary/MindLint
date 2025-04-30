from mindquantum.simulator import NoiseBackend, Simulator,get_supported_simulator
from mindquantum.core.circuit import Circuit, MeasureAccepter, MixerAdder, BitFlipAdder
circ = Circuit().h(0).x(1,0).measure_all()
print(circ)
adder = MixerAdder([
    MeasureAccepter(),
    BitFlipAdder(0.2),
], add_after=False)

noise_sim = Simulator(NoiseBackend('mqvector', 3, adder = adder))
result = noise_sim.sampling(circ,seed=42, shots=5000)
print(result)
print(get_supported_simulator())
