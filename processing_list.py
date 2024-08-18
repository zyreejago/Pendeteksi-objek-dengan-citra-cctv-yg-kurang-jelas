import PySimpleGUI as sg
import os
from PIL import Image, ImageOps
import math as m
import numpy as np

# Fungsi-fungsi untuk pemrosesan gambar
def ImgBrightness(img_input, coldepth, brightVal):
    """
    Fungsi untuk menyesuaikan kecerahan gambar.

    Parameters:
        img_input (PIL.Image): Gambar input.
        coldepth (int): Kedalaman warna gambar.
        brightVal (int): Nilai kecerahan yang akan ditambahkan pada setiap komponen warna (r, g, b).

    Returns:
        PIL.Image: Gambar yang telah disesuaikan kecerahannya.
    """
    if coldepth != 24:
        img_input = img_input.convert('RGB')

        img_output = Image.new('RGB', (img_input.size[0], img_input.size[1]))
        pixels = img_output.load()

        for i in range(img_output.size[0]):
            for j in range(img_output.size[1]):
                r, g, b = img_input.getpixel((i, j))
                # Tambahkan nilai kecerahan pada setiap komponen warna, dengan batasan maksimal 255
                pixels[i, j] = (min(brightVal + r, 255), min(brightVal + g, 255), min(brightVal + b, 255))

    else:
        img_output = img_input.point(lambda p: min(p + brightVal, 255))

    if coldepth == 1:
        img_output = img_output.convert("1")
    elif coldepth == 8:
        img_output = img_output.convert("L")
    else:
        img_output = img_output.convert("RGB")

    return img_output

def Median(img_input, coldepth, size):
    """
    Fungsi untuk filter median.

    Parameters:
        img_input (PIL.Image): Gambar input.
        coldepth (int): Kedalaman warna gambar.
        size (int): Ukuran kernel filter median.

    Returns:
        PIL.Image: Gambar dengan filter median.
    """
    if coldepth != 24:
        img_input = img_input.convert('RGB')

    img_output = Image.new('RGB', (img_input.size[0], img_input.size[1]))
    pixels = img_output.load()

    for i in range(1, img_input.size[0] - 1):
        for j in range(1, img_input.size[1] - 1):
            mask = []
            for t in range(4):
                for a in range(size):  # kanan kiri sob
                    for b in range(size):  # atas bawah sob
                        if t == 0:
                            if not ((i - a) < 0 or (j - b) < 0):
                                mask.append(img_input.getpixel((i - a, j - b)))
                            else:
                                mask.append((0, 0, 0))
                        if t == 1:
                            if not ((i - a) < 0 or (j + b) >= (img_input.size[1] - (int(size / 2)))):
                                if not (b == 0):
                                    mask.append(img_input.getpixel((i - a, j + b)))
                                else:
                                    mask.append((0, 0, 0))
                        if t == 2:
                            if not ((j - b) < 0 or (i + a) >= (img_input.size[0] - int(size / 2))):
                                if not (a == 0):
                                    mask.append(img_input.getpixel((i + a, j - b)))
                                else:
                                    mask.append((0, 0, 0))
                        if t == 3:
                            if not ((i + a) >= (img_input.size[0] - int(size / 2)) or (
                                    (j + b) >= (img_input.size[1] - int(size / 2)))):
                                if not ((a == 0) or (b == 0)):
                                    mask.append(img_input.getpixel((i + a, j + b)))
                                else:
                                    mask.append((0, 0, 0))

            mask.sort()

            n = len(mask)
            tengah = n // 2

            pixels[i, j] = (mask[tengah])

    if coldepth == 1:
        img_output = img_output.convert("1")
    elif coldepth == 8:
        img_output = img_output.convert("L")
    else:
        img_output = img_output.convert("RGB")

    return img_output

def ImgPrewitt(img_input, coldepth):
    """
    Fungsi untuk filter Prewitt.

    Parameters:
        img_input (PIL.Image): Gambar input.
        coldepth (int): Kedalaman warna gambar.

    Returns:
        PIL.Image: Gambar dengan filter Prewitt.
    """
    if coldepth != 24:
        img_input = img_input.convert('RGB')

    row, col = img_input.size
    img_output = Image.new('RGB', (row, col))
    pixel = img_output.load()

    Px = [[-1, 0, 1], [-1, 0, 1], [-1, 0, 1]]
    Py = [[1, 1, 1], [0, 0, 0], [-1, -1, -1]]

    for i in range(1, row - 1):
        for j in range(1, col - 1):
            sum_x = 0
            sum_y = 0

            for m in range(3):
                for n in range(3):
                    pixel_value = img_input.getpixel((i - 1 + m, j - 1 + n))
                    sum_x += Px[m][n] * pixel_value[0]
                    sum_y += Py[m][n] * pixel_value[0]

            gradient_pixel = int((sum_x ** 2 + sum_y ** 2) ** 0.5)
            gradient_pixel = max(0, min(gradient_pixel, 255))

            pixel[i, j] = (gradient_pixel, gradient_pixel, gradient_pixel)

    if coldepth == 1:
        img_output = img_output.convert('1')
    elif coldepth == 8:
        img_output = img_output.convert('L')
    else:
        img_output = img_output.convert('RGB')

    return img_output

def combined_brightness_prewitt(img_input, coldepth, brightVal, size):
    """
    Fungsi untuk menggabungkan filter kecerahan (Brightness) dan filter Prewitt.

    Parameters:
        img_input (PIL.Image): Gambar input.
        coldepth (int): Kedalaman warna gambar.
        brightVal (int): Nilai kecerahan yang akan ditambahkan pada setiap komponen warna (r, g, b).

    Returns:
        PIL.Image: Gambar yang telah diberi efek kecerahan dan filter Prewitt.
    """
    img_brightness = ImgBrightness(img_input, coldepth, brightVal)
    img_median = Median(img_input, coldepth, size)
    img_prewitt = ImgPrewitt(img_brightness, coldepth)
    return img_prewitt

def ObjectDetection(img_input, threshold):
    """
    Fungsi untuk deteksi objek dalam citra dengan menggunakan threshold.

    Parameters:
        img_input (PIL.Image): Gambar input dalam format PIL.
        threshold (int): Nilai ambang untuk deteksi objek.

    Returns:
        bool: True jika terdapat objek, False jika tidak.
    """
    # Konversi gambar ke grayscale jika belum grayscale
    img_gray = img_input.convert("L")

    # Ambil data piksel dari gambar
    pixels = img_gray.load()

    width, height = img_gray.size

    # Hitung jumlah piksel yang melebihi nilai ambang
    object_pixels = sum(1 for i in range(width) for j in range(height) if pixels[i, j] > threshold)

    # Tentukan apakah terdapat objek berdasarkan jumlah piksel yang terdeteksi
    return object_pixels > 0