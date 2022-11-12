from qiskit import Aer, IBMQ, transpile
from qiskit.utils import QuantumInstance
from qiskit.transpiler import PassManager
from qiskit.transpiler.passes.calibration import RZXCalibrationBuilderNoEcho
from qiskit_nature.drivers import UnitsType, Molecule
from qiskit_nature.drivers.second_quantization import ElectronicStructureDriverType, ElectronicStructureMoleculeDriver
from qiskit_nature.problems.second_quantization import ElectronicStructureProblem
from qiskit_nature.converters.second_quantization import QubitConverter
from qiskit_nature.transformers.second_quantization.electronic import FreezeCoreTransformer
from qiskit_nature.mappers.second_quantization import ParityMapper
from qiskit_nature.algorithms import GroundStateEigensolver
from qiskit_nature.runtime import VQEClient
from qiskit.algorithms import NumPyMinimumEigensolver, VQE
from qiskit.algorithms.optimizers import SPSA
from qiskit.circuit import QuantumCircuit, ParameterVector
from qiskit.utils import QuantumInstance
from qiskit.providers.aer import AerSimulator
import matplotlib.pyplot as plt
import numpy as np


backend = AerSimulator()

def HEA_naive(num_q, depth):
    circuit = QuantumCircuit(num_q)
    params = ParameterVector("theta", length=num_q * (3 * depth + 2))
    counter = 0
    for q in range(num_q):
        circuit.rx(params[counter], q)
        counter += 1
        circuit.rz(params[counter], q)
        counter += 1
    for d in range(depth):
        for q in range(num_q - 1):
            circuit.cx(q, q + 1)
        for q in range(num_q):
            circuit.rz(params[counter], q)
            counter += 1
            circuit.rx(params[counter], q)
            counter += 1
            circuit.rz(params[counter], q)
            counter += 1
    return circuit, params

def HEA_aware(num_q, depth, hardware):
    circuit = QuantumCircuit(num_q)
    params = ParameterVector("theta", length=num_q * (3 * depth + 2))
    counter = 0
    for q in range(num_q):
        circuit.rx(params[counter], q)
        counter += 1
        circuit.rz(params[counter], q)
        counter += 1
    for d in range(depth):
        for q in range(num_q - 1):
            gate = QuantumCircuit(num_q)
            gate.rzx(np.pi/2, q, q + 1)
            pass_ = RZXCalibrationBuilderNoEcho(hardware)
            qc_cr = PassManager(pass_).run(gate)
            circuit.compose(qc_cr, inplace=True)
        for q in range(num_q):
            circuit.rz(params[counter], q)
            counter += 1
            circuit.rx(params[counter], q)
            counter += 1
            circuit.rz(params[counter], q)
            counter += 1
    return circuit, params

depth = 2
qubits = 4
circuit, _ = HEA_naive(qubits, depth)
spsa = SPSA(100)
qi = QuantumInstance(Aer.get_backend('aer_simulator'))
vqe_circuit = VQE(ansatz=circuit, quantum_instance=qi, optimizer=spsa)
print(circuit)
