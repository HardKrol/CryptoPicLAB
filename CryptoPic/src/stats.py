import csv
import os
import math

import numpy as np
import matplotlib.pyplot as plt
from PIL import Image


def entropy(data):
    counts = np.bincount(data, minlength=256)
    result = 0
    for count in counts:
        if count > 0:
            p = count / len(data)
            result -= p * math.log2(p)
    return result


def correlations(img):
    arr = np.array(img.convert("L"))
    horizontal = np.corrcoef(arr[:, :-1].ravel(), arr[:, 1:].ravel())[0, 1]
    vertical = np.corrcoef(arr[:-1, :].ravel(), arr[1:, :].ravel())[0, 1]
    return horizontal, vertical


if __name__ == "__main__":
    base = os.path.dirname(os.path.dirname(__file__))
    name = "lancer"
    files = [
        ("Original", os.path.join(base, "imgs/original/" + name + ".png")),
        ("XOR", os.path.join(base, "imgs/encrypted/" + name + "_xor.png")),
        ("AES-ECB", os.path.join(base, "imgs/encrypted/" + name + "_ecb.png")),
        ("AES-CTR", os.path.join(base, "imgs/encrypted/" + name + "_ctr.png")),
    ]

    print("| Файл | Энтропия | Corr H | Corr V |")
    print("|---|---:|---:|---:|")

    images = []
    results = []
    for title, filepath in files:
        img = Image.open(filepath)
        data = np.frombuffer(img.convert("RGB").tobytes(), dtype=np.uint8)
        img_entropy = entropy(data)
        corr_h, corr_v = correlations(img)
        print("| " + title + " | " + f"{img_entropy:.4f}" + " | "
              + f"{corr_h:.4f}" + " | " + f"{corr_v:.4f}" + " |")
        results.append([title, img_entropy, corr_h, corr_v])
        images.append((title, img.convert("L")))

    fig, axes = plt.subplots(2, 2, figsize=(10, 8))
    for ax, (title, img) in zip(axes.ravel(), images):
        pixels = np.array(img).ravel()
        ax.hist(pixels, bins=256, range=(0, 256))
        ax.set_title(title)
        ax.set_xlabel("Значение пикселя")
        ax.set_ylabel("Количество")

    plt.tight_layout()
    result_path = os.path.join(base, "results/histograms.png")
    plt.savefig(result_path)
    plt.close()

    csv_path = os.path.join(base, "results/metrics.csv")
    with open(csv_path, "w", newline="", encoding="utf-8") as file:
        writer = csv.writer(file)
        writer.writerow(["Файл", "Энтропия", "Corr H", "Corr V"])
        writer.writerows(results)
