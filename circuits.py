from qiskit import *
from oracle_generation import generate_oracle

get_bin = lambda x, n: format(x, 'b').zfill(n)

def gen_circuits(min,max,size):
  circuits = []
  secrets = []

  ORACLE_SIZE = size
  for i in range(min,max+1):
    cur_str = get_bin(i,ORACLE_SIZE-1)
    (circuit, secret) = generate_oracle(ORACLE_SIZE,False,3,cur_str)
    circuits.append(circuit)
    secrets.append(secret)
  
  return (circuits, secrets)
