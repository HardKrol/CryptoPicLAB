import json
import os

from cryptography.hazmat.primitives.ciphers import Cipher, algorithms, modes
from cryptography.hazmat.primitives import padding
from PIL import Image


def add_padding(data):
    if len(data) % 16 == 0:
        return data
    padder = padding.PKCS7(algorithms.AES.block_size).padder()
    return padder.update(data) + padder.finalize()


def remove_padding(data):
    pad_size = data[-1]
    if pad_size > 0 and pad_size <= 16 and data[-pad_size:] == bytes([pad_size]) * pad_size:
        unpadder = padding.PKCS7(algorithms.AES.block_size).unpadder()
        return unpadder.update(data) + unpadder.finalize()
    return data


def encrypt_ecb(source, destination, key):
    img = Image.open(source).convert("RGB")
    data = img.tobytes()
    data = add_padding(data)
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
    res_bytes = remove_padding(res_bytes)
    Image.frombytes("RGB", img.size, res_bytes).save(destination)


def encrypt_ctr(source, destination, key):
    nonce = os.urandom(16)
    img = Image.open(source).convert("RGB")
    data = img.tobytes()
    data = add_padding(data)
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
    res_bytes = remove_padding(res_bytes)
    Image.frombytes("RGB", img.size, res_bytes).save(destination)


def save_ctr_metadata(source, nonce):
    results_file = os.path.join(os.path.dirname(os.path.dirname(__file__)), "results/meta.json")
    if os.path.exists(results_file):
        with open(results_file, "r", encoding="utf-8") as f:
            metadata = json.load(f)
    else:
        metadata = {}
    if "algorithm" in metadata:
        metadata = {}

    metadata[os.path.basename(source)] = {
        "algorithm": "aes-ctr",
        "nonce": nonce.hex(),
    }

    with open(results_file, "w", encoding="utf-8") as f:
        json.dump(metadata, f, indent=4)


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
        metadata_file = os.path.join(base, "results/meta.json")
        with open(metadata_file, "r", encoding="utf-8") as f:
            metadata = json.load(f)
        nonce = bytes.fromhex(metadata[filename]["nonce"])
        decrypt_ctr(ctr_encrypted, ctr_decrypted, key, nonce)
