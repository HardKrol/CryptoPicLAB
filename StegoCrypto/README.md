# StegoCrypto

Лабораторная работа №2: Стеганография, шифрование и статистический анализ.

## Зависимости
`pip install Pillow cryptography numpy scipy scikit-image matplotlib`

## Структура
- `src/lsb_plain.py` — обычное LSB-встраивание и извлечение.
- `src/lsb_crypto.py` — гибридное встраивание (AES-CTR шифрование) и рандомизация позиций.
- `src/stats.py` — скрипт для расчета PSNR, SSIM, Хи-квадрат и генерации графиков.

## Примеры запуска
1. Обычный LSB:
   `python src/lsb_plain.py` (внутри прописан тест встраивания и извлечения).
2. Гибридный режим (шифрование + случайные позиции):
   `python src/lsb_crypto.py`
3. Снятие метрик:
   `python src/stats.py`