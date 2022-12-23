from qiskit import *
from qiskit.tools.monitor import job_monitor
from qiskit.providers.ibmq import least_busy
import random

from oracle_generation import validate_oracle


def run_on_simulator(circuit, expected):
  simulator = Aer.get_backend('qasm_simulator')
  COUNT = 1024
  results = execute(circuit, backend = simulator, shots=COUNT).result()
  validate_oracle(results,expected,COUNT)
  return results

def run_on_QC(circuits, secrets, qubit_cnt, ibm_computer = ""):
  
  COUNT = 10000
  if not account_loaded:
    load_account()
  
  provider = IBMQ.get_provider(hub = 'ibm-q')
  # print(provider.backends())
  small_devices = provider.backends(filters=lambda x: x.configuration().n_qubits == qubit_cnt
                                   and not x.configuration().simulator)
  device = least_busy(small_devices)
  if ibm_computer != "":
    device = provider.get_backend(ibm_computer)

  current_jobs = device.active_jobs()
  job_cnt = len(current_jobs)
  # print(job_cnt)
  # print(device.remaining_jobs_count())
  print("running %d jobs..."%(len(circuits)))

  if (len(circuits) > device.remaining_jobs_count()):
    print("Too many jobs to handle (limit of %d)... Getting status of older jobs"%(device.remaining_jobs_count()))
    print("%d of the inputted circuits will not be run until older jobs are finished"%(len(circuits) - device.remaining_jobs_count()))

  while len(circuits) > 0:
    # load up to limit of jobs
    if (device.remaining_jobs_count() == 0): break
    circuit = circuits.pop(0)
    secret_key = secrets.pop(0)
    # print(secret_key)
    cur_job = execute(circuit,backend = device,shots = COUNT)
    cur_job.update_tags(replacement_tags=[secret_key])
    job_cnt+=1

  current_jobs = device.active_jobs()
  current_jobs.reverse()
  res = []
  for i in range(job_cnt):
    print("JOB %d"%(i))
    cur_job = current_jobs[i]
    job_monitor(cur_job)
    results = cur_job
    res.append(results)
    if len(circuits) > 0:
      circuit = circuits.pop(0)
      secret_key = secrets.pop(0)
      extra_job = execute(circuit,backend = device,shots = COUNT)
      extra_job.update_tags(replacement_tags=[secret_key])
      current_jobs.append(extra_job)
      job_cnt+=1
  
  return res
