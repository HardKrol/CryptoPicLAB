import os

from cryptography.hazmat.primitives.ciphers import Cipher, algorithms, modes
from PIL import Image


def encrypt_data(data, key, nonce):
    cipher = Cipher(algorithms.AES(key), modes.CTR(nonce))
    enc = cipher.encryptor()
    return enc.update(data) + enc.finalize()


def npcr(data1, data2):
    different = 0
    for i in range(len(data1)):
        if data1[i] != data2[i]:
            different += 1
    return different / len(data1) * 100


def uaci(data1, data2):
    total = 0
    for i in range(len(data1)):
        total += abs(data1[i] - data2[i]) / 255
    return total / len(data1) * 100


if __name__ == "__main__":
    base = os.path.dirname(os.path.dirname(__file__))
    source = os.path.join(base, "imgs/original/lancer.png")

    img = Image.open(source).convert("RGB")
    data = img.tobytes()

    k1 = b"0123456789abcdef0123456789abcdef"
    k2 = bytearray(k1)
    k2[0] ^= 1
    k2 = bytes(k2)

    nonce = os.urandom(16)
    c1 = encrypt_data(data, k1, nonce)
    c2 = encrypt_data(data, k2, nonce)

    print("NPCR:", npcr(c1, c2), "%")
    print("UACI:", uaci(c1, c2), "%")
