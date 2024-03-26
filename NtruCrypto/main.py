from NtruCrypto import Ntru1
from NTRUCryptoNp import Ntru
import matplotlib.pyplot as plt
import time 
import numpy as np
NTRU_N = 11
NTRU_p = 3
NTRU_q = 251

if __name__ == "__main__":

    nt1 = Ntru1(NTRU_N, NTRU_p, NTRU_q)
    nt = Ntru(NTRU_N, NTRU_p, NTRU_q)
    
    nt.key_gen(3)
    nt1.key_gen(3)
    err = 0
    times = []
    times1 = []

    
    for r in range(1 << NTRU_N):

        start_time = 0
        used_time = 0
        count = 0

        for i in range(1 << NTRU_N):
            
            cx = nt1.encrypt(i, 121)
            start_time = time.time_ns()
            mx = nt1.decrypt(cx)
            end_time = time.time_ns()
            if mx != i:
                err += 1
            
            count+=1
            c = nt1.poly("", cx)
            # print(f"m:{i:4d} | cx:{c} | decrypt:{mx:4d}, r:{r} | errs:{err:7d}")
            used_time += (end_time - start_time)

        times1.append((used_time / count / 1000))

        print(f"Ntru De average spent {(used_time) / count/ 1000:20f} us | r:{r} | errors:{err}")
        # print(f"Ntru En and De average spent {(end_time - start_time) / count:20f} us")




    for r in range(1 << NTRU_N):

        start_time = 0
        used_time = 0
        count = 0

        for i in range(1 << NTRU_N):
            
            cx = nt.encrypt(i, 121)
            start_time = time.time_ns()
            mx = nt.decrypt(cx)
            end_time = time.time_ns()
            if mx != i:
                err += 1
            
            count+=1
            c = nt.poly("", cx)
            # print(f"m:{i:4d} | cx:{c} | decrypt:{mx:4d}, r:{r} | errs:{err:7d}")
            used_time += (end_time - start_time)

        times.append((used_time / count / 1000))

        print(f"Ntru De average spent {(used_time) / count/ 1000:20f} us | r:{r} | errors:{err}")
        # print(f"Ntru En and De average spent {(end_time - start_time) / count:20f} us")
    
    r_range = range(0, (1 << NTRU_N))

    print(f"ntru1 average spent {np.mean(times1)}us")
    print(f"ntru average spent {np.mean(times)}us")
    plt.plot(r_range, times1, color = 'r', label='ntru')
    plt.plot(r_range, times, color = 'b', label='ntru-conv')
    plt.ylim(0, 1000)
    plt.xlabel('r')
    plt.ylabel('us')
    plt.title('spent time')
    plt.show()

    
    
    
    
    

    