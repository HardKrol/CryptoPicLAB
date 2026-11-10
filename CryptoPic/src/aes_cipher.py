import json
import os

from cryptography.hazmat.primitives.ciphers import Cipher, algorithms, modes
from PIL import Image


def encrypt_ecb(source, destination, key):
    img = Image.open(source).convert("RGB")
    data = img.tobytes()
    cipher = Cipher(algorithms.AES(key), modes.ECB())
    enc = cipher.encryptor()
    res_bytes = enc.update(data) + enc.finalize()
    Image.frombytes("RGB", img.size, res_bytes).save(destination)


def decrypt_ecb(source, destination, key):
    img = Image.open(source).convert("RGB")
    data = img.tobytes()
    cipher = Cipher(algorithms.AES(key), modes.ECB())
    dec = cipher.decryptor()
    res_bytes = dec.update(data) + dec.finalize()
    Image.frombytes("RGB", img.size, res_bytes).save(destination)


def encrypt_ctr(source, destination, key):
    nonce = os.urandom(16)
    img = Image.open(source).convert("RGB")
    data = img.tobytes()
    cipher = Cipher(algorithms.AES(key), modes.CTR(nonce))
    enc = cipher.encryptor()
    res_bytes = enc.update(data) + enc.finalize()
    Image.frombytes("RGB", img.size, res_bytes).save(destination)
    return nonce


def decrypt_ctr(source, destination, key, nonce):
    img = Image.open(source).convert("RGB")
    data = img.tobytes()
    cipher = Cipher(algorithms.AES(key), modes.CTR(nonce))
    dec = cipher.decryptor()
    res_bytes = dec.update(data) + dec.finalize()
    Image.frombytes("RGB", img.size, res_bytes).save(destination)


def save_ctr_metadata(source, nonce):
    metadata = {
        "algorithm": "aes-ctr",
        "nonce": nonce.hex(),
        "source": os.path.basename(source),
    }
    results_file = os.path.join(os.path.dirname(os.path.dirname(__file__)), "results/meta.json")
    with open(results_file, "w", encoding="utf-8") as f:
        json.dump(metadata, f)


if __name__ == "__main__":
    key = b"0123456789abcdef0123456789abcdef"
    base = os.path.dirname(os.path.dirname(__file__))

    files = ["checkerboard.png", "gradient.png", "lancer.png"]
    for filename in files:
        source = os.path.join(base, "imgs/original", filename)
        name = filename.rsplit(".", 1)[0]

        ecb_encrypted = os.path.join(base, "imgs/encrypted", name + "_ecb.png")
        ecb_decrypted = os.path.join(base, "imgs/decrypted", name + "_ecb.png")
        encrypt_ecb(source, ecb_encrypted, key)
        decrypt_ecb(ecb_encrypted, ecb_decrypted, key)

        ctr_encrypted = os.path.join(base, "imgs/encrypted", name + "_ctr.png")
        ctr_decrypted = os.path.join(base, "imgs/decrypted", name + "_ctr.png")
        nonce = encrypt_ctr(source, ctr_encrypted, key)
        save_ctr_metadata(source, nonce)
        decrypt_ctr(ctr_encrypted, ctr_decrypted, key, nonce)
