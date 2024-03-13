from NtruCrypto import PolyObj, Ntru
import matplotlib.pyplot as plt
import time 

NTRU_N = 11
NTRU_p = 3
NTRU_q = 251

if __name__ == "__main__":

    nt = Ntru(NTRU_N, NTRU_p, NTRU_q)
    nt.key_gen(3)
    err = 0
    times = []
    for r in range(1 << NTRU_N):

        start_time = time.time_ns()
        count = 0

        for i in range(1 << NTRU_N):
            cx = nt.encrypt(i, 121)
            mx = nt.decrypt(cx)
            if mx != i:
                err += 1
            count+=1
            c = nt.poly("", cx)
            # print(f"m:{i:4d} | cx:{c} | decrypt:{mx:4d}, errs:{err:7d}")
            
        end_time = time.time_ns()
        used_time = end_time - start_time
        times.append((used_time / count / 1000))

        print(f"Ntru En and De average spent {(end_time - start_time) / count:20f} us | errors:{err}")

    r_range = range(0, (1 << NTRU_N))
    plt.plot(r_range, times)
    plt.ylim(0, 1000)
    plt.xlabel('r')
    plt.ylabel('us')
    plt.title('spent time')
    plt.show()