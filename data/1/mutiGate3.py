from mindquantum.simulator import NoiseBackend, Simulator
from mindquantum.core.circuit import Circuit, MeasureAccepter, MixerAdder, BitFlipAdder
circ = Circuit().h(0).x(0).measure_all()
Circuit().h(0).cx(1,0)
print(circ)
adder = MixerAdder([
    MeasureAccepter(),
    BitFlipAdder(0.2),
], add_after=False)

noise_sim = Simulator(NoiseBackend('mqvector', 1, adder = adder))
result = noise_sim.sampling(circ,seed=42, shots=5000)
print(result)