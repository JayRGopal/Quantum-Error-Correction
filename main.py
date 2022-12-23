from qiskit import *
from qiskit.tools.monitor import job_monitor
from qiskit.providers.ibmq import least_busy
from qiskit.tools.visualization import plot_histogram, array_to_latex
from qiskit.utils.mitigation import complete_meas_cal, CompleteMeasFitter

import numpy as np
import scipy.linalg as la
import random

import matplotlib.pyplot as plt

from oracle_generation import generate_oracle, validate_oracle
from devices import run_on_simulator, run_on_QC
from circuits import get_bin, gen_circuits
from error_matrix import Minv, diags
from helpers import fix_to_full_hist, correct_results, get_avg, get_job_by_tag

key = 'INSERT IBMQ KEY HERE'

account_loaded = False
def load_account():
  IBMQ.save_account(key,overwrite=True)
  IBMQ.load_account() # Load account from disk
  provider = IBMQ.get_provider(hub = 'ibm-q')
  account_loaded = True


if __name__ == '__main__':
  # Load the account
  load_account()


  # Generate the oracle and secret key
  (circuit, secret_key) = generate_oracle(6,False,3)
  print("Secret Key: ", secret_key)


  # Visualize the circuit
  circuit.draw()


  # Get results on two different devices
  results_simulator = run_on_simulator(circuit,secret_key)
  plot_histogram(results_simulator)

  results_QC = run_on_QC([circuit])
  plot_histogram(results_QC)


  # Generate quantum circuits
  CNT = 10000
  ORACLE_SIZE = 5
  (circuits,secrets) = gen_circuits(0,0,ORACLE_SIZE)
  print(secrets)


  # Run jobs on quantum computer
  finished_jobs = run_on_QC(circuits,secrets,ORACLE_SIZE,"ibmq_quito")
  for job in finished_jobs:
    result = job.result()
    counts = result.get_counts()
    expected = job.tags()[0] if len(job.tags()) > 0 else counts.most_frequent()
    validate_oracle(counts,expected,CNT)

  
  # Accuracies
  acc_by_cnot_cnt = {}

  for i in range(len(diags)):
    cur_diag = diags[i]
    bin_i = get_bin(i,ORACLE_SIZE)
    num_cnot = bin_i.count("1")

    if num_cnot not in acc_by_cnot_cnt:
      acc_by_cnot_cnt[num_cnot] = [cur_diag]
    else:
      acc_by_cnot_cnt[num_cnot].append(cur_diag)

  final_dict = {}
  for (num_cnot, accs) in acc_by_cnot_cnt.items():
    final_dict[num_cnot] = get_avg(accs)


  # Print and display final results
  print(list(final_dict.values()))

  cnts = list(final_dict.keys())
  vals = list(final_dict.values())

  plt.bar(cnts,vals)
  plt.xlabel("Number of CNOT gates")
  plt.ylabel("Accuracy (%)")
  plt.title("Average accuracy for CNOT gate count")

  plt.plot(vals)


  # Provider information 
  provider = IBMQ.get_provider(hub = 'ibm-q')
  device = provider.get_backend("ibmq_quito")


  # Generate circuits again, with max = 15
  CNT = 10000
  ORACLE_SIZE = 5
  (circuits,secrets) = gen_circuits(0,15,ORACLE_SIZE)

  for circuit in circuits:
    print(circuit)


  # Quantum Register
  qr = QuantumRegister(ORACLE_SIZE)
  SHOTS = 10000
  meas_calibs, state_labels = complete_meas_cal(qr=qr, circlabel='mcal')
  t_qc = transpile(circuits, device)
  qobj = assemble(t_qc, shots=SHOTS)
  cal_results = execute(circuit,backend = device,shots = SHOTS).result()

  print(cal_results.get_counts())
  meas_fitter = CompleteMeasFitter(cal_results, state_labels, circlabel='mcal')
  # array_to_latex(meas_fitter.cal_matrix)

  mitigated_results = meas_fitter.filter.apply(cal_results)
  mitigated_counts = mitigated_results.get_counts()
  noisy_counts = cal_results.get_counts()

  res = get_job_by_tag("1110","ibmq_quito").result()
  print(res.get_counts().values())

  hist_vert = np.vstack(list(res.get_counts().values())) / SHOTS
  error_corrected = np.matmul(Minv,hist_vert)
  # array_to_latex(error_corrected)


  # Error Correction!
  corrected_hist = {}

  for i in range(len(error_corrected)):
    cur_val = error_corrected[i]
    cur_bin = get_bin(i,ORACLE_SIZE-1) 

    corrected_hist[cur_bin] = cur_val[0] * SHOTS

  print(corrected_hist)
  print(res.get_counts())
    

  # Plot initial vs. corrected results
  plot_histogram([res.get_counts(),corrected_hist],legend=['noisy','mitigated'])

  init_results, corrected_results = [], []
  binaries = ["0000","0010","0101","1110","1111"]
  for b_str in binaries:
    print(b_str)
    cur_res, cur_corrected = correct_results(get_job_by_tag(b_str,"ibmq_quito").result())
    init_results.append(cur_res)
    corrected_results.append(cur_corrected)

  plot_histogram([init_results[0],corrected_results[0]],legend=['noisy','mitigated']) #0000

  plot_histogram([init_results[1],corrected_results[1]],legend=['noisy','mitigated']) #0010

  plot_histogram([init_results[2],corrected_results[2]],legend=['noisy','mitigated']) #0101

  plot_histogram([init_results[3],corrected_results[3]],legend=['noisy','mitigated']) #1110

  plot_histogram([init_results[4],corrected_results[4]],legend=['noisy','mitigated']) #1111