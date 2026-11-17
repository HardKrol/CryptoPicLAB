import csv
from pathlib import Path

import matplotlib.pyplot as plt
import numpy as np
from PIL import Image
from scipy.stats import chisquare
from skimage.metrics import peak_signal_noise_ratio, structural_similarity

from lsb_base import embed_lsb
from lsb_hybrid import embed_encrypted


def changed_ratio(cover, stego):
    changed_pixels = np.any(cover != stego, axis=-1)
    return np.mean(changed_pixels)


def lsb_probabilities(image):
    bits = image & 1
    probability_one = np.mean(bits)
    return 1 - probability_one, probability_one


def chi_square_pvalue(image):
    values = np.bincount(image.ravel(), minlength=256)
    expected_pairs = (values[::2] + values[1::2]) / 2
    expected = np.repeat(expected_pairs, 2)
    nonzero = expected > 0
    result = chisquare(values[nonzero], expected[nonzero])
    return result.pvalue


def calculate_metrics(cover, stego):
    probability_zero, probability_one = lsb_probabilities(stego)
    return {
        "PSNR": peak_signal_noise_ratio(cover, stego, data_range=255),
        "SSIM": structural_similarity(
            cover, stego, channel_axis=-1, data_range=255
        ),
        "Changed Ratio": changed_ratio(cover, stego),
        "P(LSB=1)": probability_one,
        "Chi-square p-value": chi_square_pvalue(stego),
    }


def print_table(image_name, payload_name, results):
    print(f"\n### {image_name} — {payload_name}\n")
    print("| Method | PSNR | SSIM | Changed Ratio | P(LSB=1) | Chi-square p-value |")
    print("|---|---:|---:|---:|---:|---:|")
    for method, metrics in results.items():
        print(
            f"| {method} | {metrics['PSNR']:.4f} | "
            f"{metrics['SSIM']:.6f} | {metrics['Changed Ratio']:.6f} | "
            f"{metrics['P(LSB=1)']:.6f} | "
            f"{metrics['Chi-square p-value']:.6g} |"
        )


def main():
    project_dir = Path(__file__).resolve().parent.parent
    image_paths = [
        project_dir / "imgs" / "lancer.png",
        project_dir / "imgs" / "gradient.png",
    ]
    results_dir = project_dir / "results"
    results_dir.mkdir(exist_ok=True)

    payloads = {
        "1% payload": "О Великий Root и Святой localhost, изгони двоичного демона из моей оперативной памяти. Во имя Гита, Питона и Святого Докера. Enter.",
        "5% payload": "О Великий Root и Святой localhost, Изгони двоичного демона из моей оперативной памяти. Отведи от меня Segmentation Fault и внезапную потерю пакетов, Спаси мои контейнеры от ошибки 137, а код — от бесконечного цикла. Да сойдутся все хэши без коллизий, и да будет аптайм мой вечным. Во имя Гита, Питона и Святого Докера. Enter."
        * 2,
    }
    password = "supersecret"
    all_rows = []

    for image_path in image_paths:
        with Image.open(image_path) as source:
            cover = np.array(source.convert("RGB"))

        for payload_name, text in payloads.items():
            methods = {
                "Plain LSB": lambda path: embed_lsb(image_path, path, text),
                "Encrypted LSB": lambda path: embed_encrypted(
                    image_path, path, password, text
                ),
                "Random LSB": lambda path: embed_encrypted(
                    image_path, path, password, text, use_random=True
                ),
            }
            metrics = {}
            for method_name, embed in methods.items():
                stego_path = results_dir / (
                    f"{image_path.stem}_{payload_name[:2]}_{method_name}.png"
                )
                embed(stego_path)
                with Image.open(stego_path) as stego_image:
                    stego = np.array(stego_image.convert("RGB"))
                metrics[method_name] = calculate_metrics(cover, stego)
                all_rows.append(
                    {
                        "Image": image_path.name,
                        "Payload": payload_name,
                        "Method": method_name,
                        **metrics[method_name],
                    }
                )

                if (
                    image_path.name == "lancer.png"
                    and payload_name == "5% payload"
                    and method_name == "Plain LSB"
                ):
                    difference = np.abs(
                        cover.astype(np.int16) - stego.astype(np.int16)
                    )
                    difference = np.clip(difference * 255, 0, 255).astype(np.uint8)
                    Image.fromarray(difference).save(results_dir / "difference.png")

                    figure, axes = plt.subplots(1, 2, figsize=(12, 4))
                    axes[0].hist(cover.ravel(), bins=256, range=(0, 255), alpha=0.6)
                    axes[0].set_title("Cover")
                    axes[1].hist(stego.ravel(), bins=256, range=(0, 255), alpha=0.6)
                    axes[1].set_title("Stego")
                    for axis in axes:
                        axis.set_xlabel("Pixel value")
                        axis.set_ylabel("Count")
                    figure.tight_layout()
                    figure.savefig(results_dir / "histogram.png")
                    plt.close(figure)

            print_table(image_path.name, payload_name, metrics)

    with open(results_dir / "metrics.csv", "w", newline="") as csv_file:
        writer = csv.DictWriter(
            csv_file,
            fieldnames=[
                "Image",
                "Payload",
                "Method",
                "PSNR",
                "SSIM",
                "Changed Ratio",
                "P(LSB=1)",
                "Chi-square p-value",
            ],
        )
        writer.writeheader()
        writer.writerows(all_rows)


if __name__ == "__main__":
    main()
