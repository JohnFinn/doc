from os import walk, getcwd
from string import ascii_lowercase, ascii_uppercase
from PIL import Image, ImageFont, ImageDraw
from csv import writer


def generate_letter_image(letter, row_writer, alphabet):
    for font_file in next(walk(getcwd() + '/fonts'))[2]:
        img = Image.new('L', (32, 32), 'white')
        font = ImageFont.truetype(getcwd() + '/fonts/' + font_file, 32)
        draw = ImageDraw.Draw(img)
        w, h = draw.textsize(letter, font=font)
        draw.text(((img.width - w) / 2, (img.height - h) / 2), letter, font=font, fill='black')
        for i in range(13):
            for angle in range(-10, 10, 1):
                rot_im = img.rotate(angle, expand=False, fillcolor='white')
                filepath = f'dataset_letters/{letter}_{alphabet}_{angle}_{font_file[:-4]}_{i}.png'
                rot_im.save(filepath, 'PNG')
                row_writer.writerow([filepath, letter])


def main():
    with open(getcwd() + '/letters.csv', 'w') as file:
        row_writer = writer(file, delimiter=',')
        row_writer.writerow(['filepath', 'letter'])
        for i in list(ascii_lowercase):
            generate_letter_image(i, row_writer, 'l')
        for i in list(ascii_uppercase):
            generate_letter_image(i, row_writer, 'l')
        cyrillic_unique_upper = 'БГДЁЖЗИЙЛПФЦЧШЩЪЫЬЭЮЯ'
        cyrillic_unique_lower = 'бгдёжзиймнптфцчшщъыьэюя'
        for letter in cyrillic_unique_upper:
            generate_letter_image(letter, row_writer, 'c')
        for letter in cyrillic_unique_lower:
            generate_letter_image(letter, row_writer, 'c')


if __name__ == '__main__':
    main()

