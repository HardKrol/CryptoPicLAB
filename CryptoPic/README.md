# CryptoPic

Лабораторная работа №1: Шифрование изображений и статистическое сравнение методов.

## Зависимости
- Python 3.9+
- Pillow
- cryptography
- numpy
- matplotlib

Установка зависимостей:
`pip install Pillow cryptography numpy matplotlib`

## Запуск
1. `python src/xor_cipher.py` — потоковое шифрование (XOR).
2. `python src/aes_cipher.py` — шифрование AES (ECB и CTR).
3. `python src/verify.py` — проверка обратимости (совпадение SHA-256).
4. `python src/stats.py` — расчет энтропии, корреляции и построение гистограмм.
5. `python src/key_sensitivity.py` — расчет NPCR и UACI при изменении ключа.

Реализованные алгоритмы: кастомный XOR (на базе xorshift32), AES-ECB, AES-CTR.