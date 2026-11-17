import os

from PIL import Image


def xorshift32(state):
    state &= 0xFFFFFFFF
    state ^= (state << 13) & 0xFFFFFFFF
    state ^= state >> 17
    state ^= (state << 5) & 0xFFFFFFFF
    return state & 0xFFFFFFFF


def xor_cipher(data, key):
    state = key
    arr = bytearray()
    for byte in data:
        state = xorshift32(state)
        arr.append(byte ^ (state & 0xFF))
    return bytes(arr)


def process_image(source, destination, key):
    img = Image.open(source).convert("RGB")
    data = img.tobytes()
    res_bytes = xor_cipher(data, key)
    new_img = Image.frombytes("RGB", img.size, res_bytes)
    new_img.save(destination)


if __name__ == "__main__":
    key = 123456
    base = os.path.dirname(os.path.dirname(__file__))
    files = ["checkerboard.png", "gradient.png", "lancer.png"]

    for filename in files:
        source = os.path.join(base, "imgs/original", filename)
        name = filename.rsplit(".", 1)[0]
        encrypted = os.path.join(base, "imgs/encrypted", name + "_xor.png")
        decrypted = os.path.join(base, "imgs/decrypted", name + "_xor.png")

        process_image(source, encrypted, key)
        process_image(encrypted, decrypted, key)
