from qiskit import *

import random



def generate_oracle(oracle_length, random_cnot, cnot_count, fixed_string=""):

  if random_cnot == True:
    cnot_count = random.randint(0, oracle_length)

  random_cnots = random.sample(range(0, oracle_length), cnot_count)

  oracle = ""

  for i in range(oracle_length):
    if random_cnots.count(i) == 1:
      oracle = oracle + "1"
    else:
      oracle = oracle + "0"

  if fixed_string != "" and len(fixed_string) == oracle_length - 1:
    oracle = fixed_string

  circuit = QuantumCircuit(len(oracle)+1, len(oracle))

  circuit.h(range(len(oracle)))

  circuit.x(len(oracle))
  circuit.h(len(oracle))

  circuit.barrier()

  for ii, yesno in enumerate(reversed(oracle)):
    if yesno == '1':
      circuit.cx(ii, len(oracle))

  circuit.barrier()

  circuit.h(range(len(oracle)))

  circuit.barrier()

  circuit.measure(range(len(oracle)), range(len(oracle)))

  return [circuit, oracle]

def validate_oracle(results,expected,cnt):
  print("ORACLE PASSES :)" if results.get_counts().most_frequent() == expected else "oracle failed... :(")
  acc = (results.get_counts()[expected] / cnt) * 100
  print("Correct with %d%% accurary"%(acc))
