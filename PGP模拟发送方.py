import random
from gmssl import sm3
import socket
import json
import math
import random
from gmssl import sm3
from gmssl import sm4
import json
from gmssl.sm4 import CryptSM4, SM4_ENCRYPT, SM4_DECRYPT
import re
#SM3推荐参数：secp256r1
p=0x8542D69E4C044F18E8B92435BF6FF7DE457283915C45517D722EDB8B08F1DFC3
a=0x787968B4FA32C3FD2417842E73BBFEFF2F3C848B6831D7E0EC65228B3937E498
b=0x63E4C6D3B23B0C849CF84241484BFE48F61D59A5B16BA06E6E12D1DA27C5249A
n=0x8542D69E4C044F18E8B92435BF6FF7DD297720630485628D5AE74EE7C32E79B7
Gx=0x421DEBD61B62EAB6746434EBC3CC315E32220B3BADD50BDC4C4E6C147FEDD43D
Gy=0x0680512BCBB42C07D47349D2153B70C4E5D7FDFCBFA36EA1A85841B9E46E09A2

#print(hashlib.sha1("123".encode()).hexdigest())

def show_points(p, a, b):
    return [(x, y) for x in range(p) for y in range(p) if (y * y - (x * x * x + a * x + b)) % p == 0]


def GCD(a, b):
    if b == 0:
        return a
    else:
        return GCD(b, a % b)


def XGCD(a, b):
    if (b == 0):
        return 1, 0, a
    else:
        x, y, d = XGCD(b, a % b)
        return y, (x - (a // b) * y), d


# print(XGCD(6553215,5754840))

def get_inverse(a, b):
    return XGCD(a, b)[0] % b


def pow_mod(a, b, n):
    a = a % n
    ans = 1
    # 这里我们不需要考虑b<0，因为分数没有取模运算
    while b != 0:
        if b & 1:
            ans = (ans * a) % n
        b >>= 1
        a = (a * a) % n
    return ans


def get_miller(m):
    while (m % 2 == 0):
        m = m // 2
    return m


def rabin_miller(p):
    if p == 2:
        return True
    elif p % 2 == 0:
        return False
    else:
        m = p - 1
        m = get_miller(m)
        the_pow_mod = pow_mod(2, m, p)
        if the_pow_mod == 1:
            return True
        a = m

        while (a <= p - 1):
            the_pow_mod = the_pow_mod ** 2 % p
            if the_pow_mod == 1:
                return True
            a = a * 2
        return False


# 求最大公约数——用于约分化简
def get_gcd(x, y):
    if y == 0:
        return x
    else:
        return get_gcd(y, x % y)

    # 计算P+Q函数



def get_Qr(n,p):
    # 求勒让德符号
    def Legender(a, p):
        return pow_mod(a, (p - 1) >> 1, p)

    class T:
        p = 0
        d = 0

    w = 0

    def multi_er(a, b, m):
        ans = T()
        ans.p = (a.p * b.p % m + a.d * b.d % m * w % m) % m
        ans.d = (a.p * b.d % m + a.d * b.p % m) % m
        return ans

    def power(a, b, m):
        ans = T()
        ans.p = 1
        ans.d = 0
        while b:
            if b & 1:
                ans = multi_er(ans, a, m);
                b -= 1
            b >>= 1
            a = multi_er(a, a, m)
        return ans
    a=0
    t=0
    while True:
        a=random.randrange(1,p)
        t= a*a-n
        w = t%p
        if Legender(w,p)+1==p:
            break
    tmp=T()
    tmp.p = a
    tmp.d = 1
    ans = power(tmp, (p + 1) >> 1, p)
    if ans.p<p-ans.p:
        y1=ans.p
        y2=p-ans.p
    else:
        y1 = p-ans.p
        y2 = ans.p
    return y1,y2

def calculate_p_q(x1, y1, x2, y2, a, b, p):
    flag = 1  # 控制符号位

    # 若P = Q，则k=[(3x1^2+a)/2y1]mod p
    if x1 == x2 and y1 == y2:
        member = 3 * (x1 ** 2) + a  # 计算分子
        denominator = 2 * y1  # 计算分母

    # 若P≠Q，则k=(y2-y1)/(x2-x1) mod p
    else:
        member = y2 - y1
        denominator = x2 - x1
        if member * denominator < 0:
            flag = 0
            member = abs(member)
            denominator = abs(denominator)

    # 将分子和分母化为最简
    gcd_value = get_gcd(member, denominator)
    member = member // gcd_value
    denominator = denominator // gcd_value

    # 求分母的逆元
    inverse_value = get_inverse(denominator, p)
    k = (member * inverse_value)
    if flag == 0:
        k = -k
    k = k % p

    # 计算x3,y3
    """
        x3≡k^2-x1-x2(mod p)
        y3≡k(x1-x3)-y1(mod p)
    """
    x3 = (k ** 2 - x1 - x2) % p
    y3 = (k * (x1 - x3) - y1) % p
    return [x3, y3]


# 计算2P函数
def calculate_2p(p_x, p_y, a, b, p):
    tem_x = p_x
    tem_y = p_y
    p_value = calculate_p_q(tem_x, tem_y, p_x, p_y, a, b, p)
    tem_x = p_value[0]
    tem_y = p_value[1]
    return p_value


# 计算nP函数
def calculate_np(p_x, p_y, n, a, b, p):
    p_value = ["0", "0"]
    p_temp = [0, 0]
    # 这里我们不需要考虑b<0，因为分数没有取模运算
    while n != 0:
        if n & 1:
            if (p_value[0] == "0" and p_value[1] == "0"):
                p_value[0], p_value[1] = p_x, p_y
            else:
                p_value = calculate_p_q(p_value[0], p_value[1], p_x, p_y, a, b, p)
        n >>= 1
        p_temp = calculate_2p(p_x, p_y, a, b, p)
        p_x, p_y = p_temp[0], p_temp[1]
    return p_value

def calculate_Tp(p_x, p_y,a, b, p):
    return p_x,p-p_y

def get_key():
    dA=random.randrange(0,n)
    PA=calculate_np(Gx, Gy, dA, a, b, p)
    return dA,PA



def get_bitsize(num):
    len=0
    while num//256:
        len+=1
        num=num//256
    return len+1

def int_to_bytes(num):
    return num.to_bytes(get_bitsize(num),byteorder='big', signed=False)
def bytes_to_int(bytes):
    return int.from_bytes(bytes,byteorder='big')

def KDF(z,klen):
    ct=1
    k=''
    for i in range(int(klen/256)+1):
        k=k+sm3.sm3_hash(list(z+ct.to_bytes(4,byteorder='big', signed=False)))
        ct=ct+1
    k='0'*((256-(len(bin(int(k,16))[2:])%256))%256)+bin(int(k,16))[2:]
    return int(hex(int(k[:klen],2))[2:],16)

#num=int_to_bytes(0x64D20D27D0632957F8028C1E024F6B02EDF23102A566C932AE8BD613A8E865FE)+int_to_bytes(0x58D225ECA784AE300A81A2D48281A828E1CEDF11C4219099840265375077BF78)
#print(hex(bytes_to_int(num)))
#print(KDF(num,152))

def sm3_en(msg,P):
    k=random.randrange(1,n)
    M=bytes_to_int(msg.encode())
    klen=len(msg.encode())*8
    #print(klen)
    #print(hex(M))
    x1,y1=calculate_np(Gx, Gy, k, a, b, p)
    #print(hex(x1))
    #print(hex(y1))
    if y1<p-y1:
        PC=2
    else:
        PC=3
    C1=int_to_bytes(PC)+int_to_bytes(x1)
    C1=bytes_to_int(C1)
    #print(list(C1))
    x2,y2=calculate_np(P[0], P[1], k, a, b, p)
    #print(hex(x2))
    #print(hex(y2))
    num=int_to_bytes(x2)+int_to_bytes(y2)
    #print(hex(KDF(num, 152)))
    t=KDF(num, klen)
    C2=M^t
    #print(hex(C2))
    temp=int_to_bytes(x2)+int_to_bytes(M)+int_to_bytes(y2)
    C3=int(sm3.sm3_hash(list(temp)),16)
    #print(hex(C3))
    C=bytes_to_int((int_to_bytes(C1)+int_to_bytes(C2)+int_to_bytes(C3)))
    #print(hex(C))
    return [C1,C2,C3]

def list_to_num(list_n):
    list_n.reverse()
    num=0
    a=1
    for i in list_n:
        num+=i*a
        a=a*16
    return num

def sm3_de(ciphertext,d):
    C1,C2,C3=ciphertext
    C1=int_to_bytes(C1)
    x1 = bytes_to_int(bytes(list(C1)[1:]))
    y1=0
    Y=get_Qr(x1*x1*x1+a*x1+b,p)
    if list(C1)[0] == 2:
        y1=Y[0]
    elif list(C1)[0] == 3:
        y1=Y[1]
    x2,y2=calculate_np(x1, y1, d, a, b, p)
    klen=get_bitsize(C2)*8
    num = int_to_bytes(x2) + int_to_bytes(y2)
    # print(hex(KDF(num, 152)))
    t = KDF(num, klen)
    M=C2^t
    temp = int_to_bytes(x2) + int_to_bytes(M) + int_to_bytes(y2)
    u = int(sm3.sm3_hash(list(temp)), 16)
    if u==C3:
        return int_to_bytes(M).decode()
    #print(hex(x1),hex(y1))


def sm3_sign(msg,ID,d,P):
    M=msg.encode()
    #dA=0x128B2FA8BD433C6C068C8D803DFF79792A519A55171B1B650C23661D15897263
    #PA=0x0AE4C7798AA0F119471BEE11825BE46202BB79E2A5844495E97C04FF4DF2548A,0x7C0240F88F1CD4E16352A73C17B7F16F07353E53A176D684A9FE0C6BB798E857

    ENTL=get_bitsize(ID)*8
    data = ENTL.to_bytes(2,byteorder='big', signed=False)+int_to_bytes(ID)+int_to_bytes(a)+int_to_bytes(b)+int_to_bytes(Gx)+int_to_bytes(Gy)+int_to_bytes(P[0])+int_to_bytes(P[1])
    ZA = int(sm3.sm3_hash(list(data)),16)
    M_=int_to_bytes(ZA)+M
    e=int(sm3.sm3_hash(list(M_)),16)
    r=0
    s=0
    while 1:
        k=random.randrange(1,n)
        #k=0x6CB28D99385C175C94F94E934817663FC176D925DD72B727260DBAAE1FB2F96F
        x1,y1=calculate_np(Gx, Gy, k, a, b, p)
        r=(e+x1)%n
        s=(get_inverse(1+d,n)*(k-r*d))%n
        if s!=0 and r!=0 and r+k != n :
            break
    return [r,s]

def verif_sign(msg,sign,ID,P):
    r, s = sign
    if not(1<=r and r<=n-1) :
        return False
    if not(1<=s and s<=n-1) :
        return False
    M = msg.encode()
    ENTL = get_bitsize(ID) * 8
    data = ENTL.to_bytes(2, byteorder='big', signed=False) + int_to_bytes(ID) + int_to_bytes(a) + int_to_bytes(b) + int_to_bytes(Gx) + int_to_bytes(Gy) + int_to_bytes(P[0]) + int_to_bytes(P[1])
    ZA = int(sm3.sm3_hash(list(data)), 16)
    M_ = int_to_bytes(ZA) + M
    e = int(sm3.sm3_hash(list(M_)), 16)
    t = (r + s) % n
    if t==0 :
        return False
    SG=calculate_np(Gx, Gy, s, a, b, p)
    tG=calculate_np(P[0], P[1], t, a, b, p)
    xx,yy=calculate_p_q(SG[0],SG[1],tG[0],tG[1],a,b,p)
    R=(e+xx)%n
    if R == r:
        return True
#print(get_Qr(142312341,p))

def PGP_sender():
    key = b'dfqjlw202100460092'
    iv = b'\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00'
    crypt_sm4 = sm4.CryptSM4()
    dA,PA=get_key()
    dB, PB = get_key()
    IDA = 12345
    IDB = 54321
    msg = "dfq202100460092"
    #print(sm3_sign(msg,IDA,dA,PA))
    H=sm3.sm3_hash(list(msg.encode()))
    temp=str(sm3_sign(H,IDA,dA,PA))
    #print(temp)
    MAC=(temp+msg).encode()
    #print(MAC)
    crypt_sm4.set_key(key, SM4_ENCRYPT)
    encrypt_value = crypt_sm4.crypt_ecb(MAC)
    #print(encrypt_value)# bytes类型
    crypt_sm4.set_key(key, SM4_DECRYPT)
    MAC = crypt_sm4.crypt_ecb(encrypt_value)
    #print(MAC)
    encrypt_value=bytes_to_int(encrypt_value)
    encrypt_key=sm3_en(key.decode(),PB)
    encrypt_key=bytes_to_int(str(encrypt_key).encode())

    print("待加密的明文为："+msg)
    print("发送的加密消息：")
    print(encrypt_value)
    print(encrypt_key)
    s = socket.socket()  # 创建 socket 对象
    host = socket.gethostname()  # 获取本地主机名
    port = 12345  # 设置端口
    s.bind((host, port))  # 绑定端口
    print("等待接收方链接...")
    s.listen(5)
    c, addr = s.accept()
    print("检测到成功链接")
    c.send(str(encrypt_value).encode())
    c.send(str(encrypt_key).encode())
    c.send(str(dB).encode())
    c.send(str(len(PA)).encode())
    for s in PA:
        s=str(s)
        c.send(s.encode())
PGP_sender()
