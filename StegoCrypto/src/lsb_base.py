from pathlib import Path
import struct

from PIL import Image


def text_to_bits(text):
    data = text.encode("utf-8")
    message = struct.pack(">I", len(data)) + data
    return [
        (byte >> bit) & 1
        for byte in message
        for bit in range(7, -1, -1)
    ]


def embed_lsb(cover_path, stego_path, text):
    with Image.open(cover_path) as source:
        image = source.convert("RGB")

    bits = text_to_bits(text)
    width, height = image.size
    capacity = width * height * 3

    if len(bits) > capacity:
        raise ValueError("Сообщение не помещается в изображение")

    pixels = list(image.getdata())
    bit_index = 0
    for pixel_index, pixel in enumerate(pixels):
        channels = list(pixel)
        for channel_index in range(3):
            if bit_index >= len(bits):
                break
            channels[channel_index] = (
                channels[channel_index] & ~1
            ) | bits[bit_index]
            bit_index += 1
        pixels[pixel_index] = tuple(channels)
        if bit_index >= len(bits):
            break

    image.putdata(pixels)
    image.save(stego_path, format="PNG")


def extract_lsb(stego_path):
    with Image.open(stego_path) as source:
        image = source.convert("RGB")

    pixels = list(image.getdata())
    bits = [channel & 1 for pixel in pixels for channel in pixel]
    if len(bits) < 32:
        raise ValueError("Изображение слишком маленькое для заголовка")

    length = int.from_bytes(
        bytes(
            sum(bits[index + offset] << (7 - offset) for offset in range(8))
            for index in range(0, 32, 8)
        ),
        byteorder="big",
    )
    message_end = 32 + length * 8
    if message_end > len(bits):
        raise ValueError("Изображение не содержит полного сообщения")

    data = bytes(
        sum(bits[index + offset] << (7 - offset) for offset in range(8))
        for index in range(32, message_end, 8)
    )
    return data.decode("utf-8")


if __name__ == "__main__":
    project_dir = Path(__file__).resolve().parent.parent
    cover_path = project_dir / "imgs" / "lancer.png"
    stego_path = project_dir / "imgs" / "stego_plain.png"
    message = "О Великий Root и Святой localhost, изгони двоичного демона из моей оперативной памяти. Во имя Гита, Питона и Святого Докера. Enter."

    embed_lsb(cover_path, stego_path, message)
    print(extract_lsb(stego_path))
