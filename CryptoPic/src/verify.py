import hashlib
import os


def get_hash(filepath):
    with open(filepath, "rb") as file:
        data = file.read()
    return hashlib.sha256(data).hexdigest()


if __name__ == "__main__":
    base = os.path.dirname(os.path.dirname(__file__))
    files = ["checkerboard.png", "gradient.png", "lancer.png"]

    for filename in files:
        name = filename.rsplit(".", 1)[0]
        original = os.path.join(base, "imgs/original", filename)
        original_hash = get_hash(original)
        print("\n" + name)
        print("Оригинал:", original_hash)

        decrypted_files = [
            ("XOR", name + "_xor.png"),
            ("AES-ECB", name + "_ecb.png"),
            ("AES-CTR", name + "_ctr.png"),
        ]
        for cipher_name, decrypted_filename in decrypted_files:
            filepath = os.path.join(base, "imgs/decrypted", decrypted_filename)
            if get_hash(filepath) == original_hash:
                print(cipher_name + ": Совпадает (ОК)")
            else:
                print(cipher_name + ": Не совпадает (ОШИБКА)")
