import os.path

from PIL import Image, ImageFont, ImageDraw
from string import ascii_lowercase, ascii_uppercase
from csv import writer
from os import walk


def unique_letters_set() -> dict:
    letters = dict()
    cyr_u = 'БГДЁЖЗИЙЛПФЦЧШЩЪЫЬЭЮЯ'
    cyr_l = cyr_u.lower() + 'мнт'
    for counter, item in enumerate(ascii_lowercase + ascii_uppercase + cyr_l + cyr_u):
        letters[item] = counter
    return letters


class LetterImage:

    def __init__(self, letter: str, width: int, height: int, font: ImageFont):
        self.__image = Image.new('L', (width, height), 'white')
        draw = ImageDraw.Draw(self.__image)
        letter_width, letter_height = draw.textsize(letter, font=font)
        average = lambda x, y: (x + y) / 2
        draw.text((average(width, -letter_width), average(height, -letter_height)),
                  letter, font=font, fill='black')

    def rotate(self, angle: int):
        self.__image = self.__image.rotate(angle, expand=False, fillcolor='white')

    def save(self, filepath: str, format: str):
        self.__image.save(filepath, format)


def generate_letter_image(letter: str, row_writer, font_path: str, image_format: str, image_size: int):
    font = ImageFont.truetype(font_path, image_size)
    img = LetterImage(letter, image_size, image_size, font)
    for angle in range(-20, 21, 2):
        img.rotate(angle)
        filepath = f'dataset_letters/{letter}_{angle}_{font_path.split("/")[-1].split(".")[0]}.png'
        img.save(filepath, image_format)
        img.rotate(-angle)
        row_writer.writerow([filepath, letter])


def make_letter_dataset(fonts_directory: str, csv_file, image_format: str, image_size: int):
    with open(csv_file, 'w') as output:
        row_writer = writer(output, delimiter=',')
        for letter in unique_letters_set():
            for _, _, font_files in walk(fonts_directory):
                for font_file in font_files:
                    generate_letter_image(letter, row_writer, os.path.join(fonts_directory, font_file),
                                          image_format, image_size)
