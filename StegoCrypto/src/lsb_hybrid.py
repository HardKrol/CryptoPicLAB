from pathlib import Path
import os
import random

from cryptography.hazmat.primitives import hashes
from cryptography.hazmat.primitives.ciphers import Cipher, algorithms, modes
from cryptography.hazmat.primitives.kdf.pbkdf2 import PBKDF2HMAC
from PIL import Image


def derive_key(password_str, salt):
    kdf = PBKDF2HMAC(
        algorithm=hashes.SHA256(),
        length=32,
        salt=salt,
        iterations=100000,
    )
    return kdf.derive(password_str.encode("utf-8"))


def encrypt_data(password_str, text_str):
    salt = os.urandom(16)
    iv = os.urandom(16)
    key = derive_key(password_str, salt)
    encryptor = Cipher(
        algorithms.AES(key), modes.CTR(iv)
    ).encryptor()
    ciphertext = encryptor.update(text_str.encode("utf-8")) + encryptor.finalize()
    return len(ciphertext).to_bytes(4, "big") + salt + iv + ciphertext


def decrypt_data(password_str, data_bytes):
    if len(data_bytes) < 36:
        raise ValueError("Недостаточно данных для расшифровки")

    ciphertext_length = int.from_bytes(data_bytes[:4], "big")
    ciphertext = data_bytes[36:36 + ciphertext_length]
    if len(ciphertext) != ciphertext_length:
        raise ValueError("Данные шифротекста повреждены")

    salt = data_bytes[4:20]
    iv = data_bytes[20:36]
    key = derive_key(password_str, salt)
    decryptor = Cipher(
        algorithms.AES(key), modes.CTR(iv)
    ).decryptor()
    plaintext = decryptor.update(ciphertext) + decryptor.finalize()
    return plaintext.decode("utf-8")


def _data_to_bits(data):
    return [
        (byte >> bit) & 1
        for byte in data
        for bit in range(7, -1, -1)
    ]


def _bits_to_bytes(bits):
    return bytes(
        sum(bits[index + offset] << (7 - offset) for offset in range(8))
        for index in range(0, len(bits), 8)
    )


def _random_positions(password, capacity):
    random.seed(password)
    return random.sample(range(capacity), capacity)


def embed_encrypted(cover_path, stego_path, password, text, use_random=False):
    with Image.open(cover_path) as source:
        image = source.convert("RGB")

    bits = _data_to_bits(encrypt_data(password, text))
    width, height = image.size
    capacity = width * height * 3
    if len(bits) > capacity:
        raise ValueError("Сообщение не помещается в изображение")

    pixels = list(image.getdata())
    positions = (
        _random_positions(password, capacity)[:len(bits)]
        if use_random
        else range(len(bits))
    )
    for bit, position in zip(bits, positions):
        pixel_index, channel_index = divmod(position, 3)
        channels = list(pixels[pixel_index])
        channels[channel_index] = (channels[channel_index] & ~1) | bit
        pixels[pixel_index] = tuple(channels)

    image.putdata(pixels)
    image.save(stego_path, format="PNG")


def extract_encrypted(stego_path, password, use_random=False):
    with Image.open(stego_path) as source:
        image = source.convert("RGB")

    pixels = list(image.getdata())
    capacity = image.width * image.height * 3
    positions = (
        _random_positions(password, capacity)
        if use_random
        else range(capacity)
    )
    bits = [
        pixels[position // 3][position % 3] & 1
        for position in positions
    ]
    if len(bits) < 288:
        raise ValueError("Изображение слишком маленькое для заголовка")

    header = _bits_to_bytes(bits[:288])
    ciphertext_length = int.from_bytes(header[:4], "big")
    data_end = (36 + ciphertext_length) * 8
    if data_end > len(bits):
        raise ValueError("Изображение не содержит полного сообщения")

    return decrypt_data(password, _bits_to_bytes(bits[:data_end]))


if __name__ == "__main__":
    project_dir = Path(__file__).resolve().parent.parent
    cover_path = project_dir / "imgs" / "lancer.png"
    password = "supersecret"
    message = "О Великий Root и Святой localhost, изгони двоичного демона из моей оперативной памяти. Во имя Гита, Питона и Святого Докера. Enter."

    encrypted_path = project_dir / "imgs" / "stego_encrypted.png"
    random_path = project_dir / "imgs" / "stego_random.png"

    embed_encrypted(cover_path, encrypted_path, password, message)
    embed_encrypted(cover_path, random_path, password, message, use_random=True)
    print(extract_encrypted(encrypted_path, password))
    print(extract_encrypted(random_path, password, use_random=True))
