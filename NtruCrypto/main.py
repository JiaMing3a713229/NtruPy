from NtruCrypto import PolyObj, Ntru


NTRU_N = 3
NTRU_p = 3
NTRU_q = 251

if __name__ == "__main__":

    nt = Ntru(NTRU_N, NTRU_p, NTRU_q)
    nt.key_gen(3)

    # print(nt.dec2arr(4))
    for i in range(1 << NTRU_N):
        cx = nt.encrypt(i, 5)
        mx = nt.decrypt(cx)
        print(f"m:{i} | cx:{cx} | decrypt:{mx}")
        
    
