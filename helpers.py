from qiskit import *
from qiskit.providers.ibmq import least_busy

import numpy as np

from error_matrix import Minv, diags
from circuits import get_bin

def fix_to_full_hist(hist, ORACLE_SIZE=5):
  for i in range(2**(ORACLE_SIZE-1)):
    b_str = get_bin(i,ORACLE_SIZE-1)
    # print(b_str)
    if b_str not in hist:
      hist[b_str] = 0

  return hist

def correct_results(res, ORACLE_SIZE=5):

  fixed_hist = fix_to_full_hist(res.get_counts())
  # print(fixed_hist)
  hist_vert = np.vstack(list(fixed_hist.values()))
  # print(hist_vert)
  error_corrected = np.matmul(Minv,hist_vert)
  corrected_hist = {}
  for i in range(len(error_corrected)):
    cur_val = error_corrected[i]
    cur_bin = get_bin(i,ORACLE_SIZE-1) 

    corrected_hist[cur_bin] = cur_val[0]
  
  return fixed_hist, corrected_hist


def get_avg(accs):
  return sum(accs) / len(accs)


def get_job_by_tag(TARGET_TAG, ibm_computer = ""):
  
  if not account_loaded:
    load_account()
  
  provider = IBMQ.get_provider(hub = 'ibm-q')
  # print(provider.backends())
  small_devices = provider.backends(filters=lambda x: not x.configuration().simulator)
  device = least_busy(small_devices)
  if ibm_computer != "":
    device = provider.get_backend(ibm_computer)

  jobs = device.jobs(limit=100)

  print(jobs)

  for job in jobs:
    # print(job.tags())
    if len(job.tags()) > 0 and job.tags()[0] == TARGET_TAG:
      return job

  return None