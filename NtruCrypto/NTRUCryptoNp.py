import math
import numpy as np


NTRU_N = 11

def centered_zero(number, modulo):
        num = number % modulo
        if num >= ((modulo + 1) // 2):
            num -= modulo
        elif num <= ((-modulo - 1) // 2):
            num += modulo
        return num 

def gcd_of(a, b):
    while b != 0:
        a, b = b, a % b
    return a

def inv_of_num(num, mod_t):
    tmp_m = mod_t
    num %= mod_t
    if gcd_of(num, mod_t) != 1:
        print(f"Inverse of {num} mod {mod_t} does not exist")
        return 0

    d1, d2 = 0, 1
    r = 0

    while num != 0:
        
        q = int(mod_t / num)
        r = mod_t % num
        mod_t, num = num, r
        d = d1 - q * d2
        d1, d2 = d2, d
        
    return d1 if d1 > 0 else d1 + tmp_m

def dec2bin(number, bits):
    binary_array = [0] * bits
    index = bits - 1
    while number > 0 and index >= 0:
        binary_array[index] = number % 2
        number //= 2
        index -= 1
    return binary_array

def dec2arr(number):
    arr = [0] * NTRU_N
    if number >= (1 << NTRU_N):
        print("Error with number")
        return None
    elif number == 0:
        return [0] * NTRU_N

    bits = math.ceil(math.log2(number + 1))
    index = bits - 1
    bin_array = dec2bin(number, bits)
    for i in range(bits):
        arr[index - i] = bin_array[i]

    return arr

class PolyObj:
    def __init__(self, name, coef):

        self.poly_name = name
        self.coef = np.array(coef)
        self.buf_size = NTRU_N + 1 if (len(self.coef) > NTRU_N) else NTRU_N
        self.degree = 0
        self.init_poly()

    def init_poly(self):
        self.degree = self.buf_size - 1
        while ((self.coef[self.degree]) == 0) and ((self.degree >= 1)):
            self.degree = (self.degree - 1)

    def print(self):
        print(f"PolyObj {self.poly_name}: ", end="")
        print(" ".join([f"{c:^4d}" for c in self.coef]), end="")
        print(f" | degree: {self.degree} buffer size: {self.buf_size}")
    
    def __repr__(self):
        coef_str = " ".join([f"{c:^4d}" for c in self.coef])
        return f"PolyObj {self.poly_name}: {coef_str} | degree: {self.degree}, buffer size: {len(self.coef)}"

class Ntru:

    def __init__(self, N, p, q):
        self.params = {
            "N"     :N,
            "p"     :p,
            "q"     :q,
            "fx"    : None,
            "gx"    : None,
            "ring"  : None,
            "Fp"    : None,
            "Fq"    : None,
            "Kp"    : None
        }

        self.key_gen_flag = False

    def poly(self, name, coef):

        if len(coef) == self.params["N"] + 1:
            coef_0 = [0] * (self.params["N"] + 1)
        else:
            coef_0 = [0] * self.params["N"]

        for i in range(len(coef)):
            coef_0[i] = coef[i]

        return PolyObj(name, coef_0)

    def ring(self, name):
        coef_ring = [-1] + [0] * (self.params["N"] - 1) + [1]
        return PolyObj(name, coef_ring)

    
    def mulpoly(self, a, b, modulo_size, name):

        # Convert coefficients to NumPy arrays
        coef_a = np.array(a.coef)
        coef_b = np.array(b.coef)
        # Perform polynomial multiplication using NumPy's convolution
        ret_coef = np.convolve(coef_a, coef_b) % modulo_size
        for i in range(self.params["N"], len(ret_coef)):
            ret_coef[i % self.params["N"]] += ret_coef[i]
            
        ret_coef.resize(self.params["N"])
        ret_coef = np.array([centered_zero(c, modulo_size) for c in ret_coef])
        return PolyObj(name, ret_coef)

    def addpoly(self, a, b, modulo_size, name):

        ret_coef = [0] * self.params["N"]
        coef_a = np.pad(a.coef, (0, self.params["N"] - len(a.coef)), mode='constant')
        coef_b = np.pad(b.coef, (0, self.params["N"] - len(b.coef)), mode='constant')
        ret_coef = (coef_a + coef_b) % modulo_size
    
        return PolyObj(name, ret_coef)

    def subpoly(self, a, b, modulo_size):
        
        ret_coef = [centered_zero((a.coef[i] - b.coef[i]), modulo_size) for i in range(max(len(a.coef), len(b.coef)))]
        return PolyObj("", ret_coef)

    def divpoly(self, dividend, division, modulo_size):
        tmp_dptr = PolyObj("", dividend.coef.copy())
        tmp_sptr = PolyObj("", division.coef.copy())
        
        inv_s = inv_of_num(tmp_sptr.coef[tmp_sptr.degree], modulo_size)
        deg_q = tmp_dptr.degree - tmp_sptr.degree
        q_arr = [0] * self.params["N"]

        while tmp_dptr.degree >= tmp_sptr.degree:
            q_coef = centered_zero(tmp_dptr.coef[tmp_dptr.degree] * inv_s, modulo_size)
            for i in range(tmp_sptr.degree + 1):
                tmp_dptr.coef[i + deg_q] -= tmp_sptr.coef[i] * q_coef
                tmp_dptr.coef[i + deg_q] = centered_zero(tmp_dptr.coef[i + deg_q], modulo_size)
            if deg_q >= 0:
                q_arr[deg_q] = q_coef
                deg_q -= 1
            while tmp_dptr.coef[tmp_dptr.degree] == 0:
                tmp_dptr.degree -= 1

        if tmp_dptr.degree < 0: 
            tmp_dptr.degree += 1
        
        return [self.poly("quotient", q_arr), tmp_dptr]
        
    def coef_sum(self, Poly):
        return sum(Poly.coef)

    def exgcd_poly(self, a, b, modulo_size, name):
        d = self.poly("", [0])
        d1, d2 = self.poly("", [0]), self.poly("", [1])
        tmp_a = self.poly("", (a.coef.copy()))
        tmp_b = self.poly("", (b.coef.copy()))
        rem = self.poly("", [0])

        while self.coef_sum(rem) != 1:
            div, rem = self.divpoly(tmp_b, tmp_a, modulo_size)
            d = self.subpoly(d1, self.mulpoly(div, d2, modulo_size, ""), modulo_size)
            tmp_a, tmp_b, d1, d2 = rem, tmp_a, d2, d
        ret = self.poly(name, d.coef)

        return ret
    
    def __encoder(self, num, name):
        coef = dec2arr(num)
        return self.poly(name, coef)

    def __decoder(self, poly_obj):
        return sum([poly_obj.coef[i] * (1 << i) for i in range(self.params["N"])])


    def check_key(self):
        val_Fp = self.mulpoly(self.params["Fp"], self.params["fx"], self.params["p"], "")
        val_Fq = self.mulpoly(self.params["Fq"], self.params["fx"], self.params["q"], "")
        tar = PolyObj("target", [1] + [0] * (self.params["N"] - 1))
        ptr_sub_fp = self.subpoly(tar, val_Fp, self.params["p"])
        ptr_sub_fq = self.subpoly(tar, val_Fq, self.params["q"])
        if self.coef_sum(ptr_sub_fp) != 0:
            print("Generating Kp failed")
            return -1
        if self.coef_sum(ptr_sub_fq) != 0:
            print("Generating Kq failed")
            return -1
        print("Generating Key Succeeded")
        return 1


    def key_gen(self, g_num):
        
        coef_f = [-1, -1, -1, -1, -1, 1, 1, 1, 1, 1, 1]
        # coef_f = [1, 1, -1]
        self.params["gx"] = self.__encoder(g_num, "gx")
        if not self.key_gen_flag:
            self.params["fx"] = self.poly("fx", coef_f)
            self.params["ring"] = self.ring("ring")
            self.params["Fp"] = self.exgcd_poly(self.params["fx"], self.params["ring"], self.params["p"], "Fp")
            self.params["Fq"] = self.exgcd_poly(self.params["fx"], self.params["ring"], self.params["q"], "Fq")
            self.key_gen_flag = True
        self.params["Kp"] = self.mulpoly(self.params["Fq"], self.params["gx"], self.params["q"], "kp")
        
        print(self.params["fx"])
        print(self.params["ring"])
        print(self.params["Fp"])
        print(self.params["Fq"])
        print(self.params["Kp"])
        print(self.params["gx"])

        if self.check_key() == -1:
            return -1
        return 1

    def encrypt(self, num, randnum):
        rx = self.__encoder(randnum, "rx")
        ret_poly = self.mulpoly(self.params["Kp"], rx, self.params["q"], "")
        for i in range(self.params["N"]):
            ret_poly.coef[i] *= self.params["p"]
            ret_poly.coef[i] %= self.params["q"]    
        mx = self.__encoder(num, "m")
        ret_poly = self.addpoly(ret_poly, mx, self.params["q"], "cx")
        
        for i in range(self.params["N"]):
            ret_poly.coef[i] = centered_zero(ret_poly.coef[i], self.params["q"])

        return ret_poly.coef

    def decrypt(self, cx_coef):
        cx = self.poly("cx", cx_coef)
        ax = self.mulpoly(cx, self.params["fx"], self.params["q"], "ax")
        ret = self.mulpoly(self.params["Fp"], ax, self.params["p"], "mx")
        return self.__decoder(ret)