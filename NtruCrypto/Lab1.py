from NTRUCryptoNp import Ntru
import matplotlib.pyplot as plt
import time 
import numpy as np
NTRU_N = 11
NTRU_p = 3
NTRU_q = 251


if __name__ == "__main__":

    
    nt = Ntru(NTRU_N, NTRU_p, NTRU_q)
    
    nt.key_gen(3)

    n = 2
    buffer_ct = np.zeros((n, NTRU_N), dtype = np.int32)
    buffer_pt = np.zeros(n, dtype = np.int32)
    f_kernel = np.zeros((n, NTRU_N), dtype= np.int32)
    
    
    