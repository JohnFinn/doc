import cv2
import numpy as np
from skimage.filters import threshold_yen
from skimage.exposure import rescale_intensity
from scipy.signal import argrelextrema


def image_preparation(image: np.ndarray, xscale, yscale):
    image = cv2.cvtColor(image, cv2.COLOR_BGR2GRAY)
    image = rescale_intensity(image, (0, threshold_yen(image)), (0, 255))
    thresh_img = cv2.erode(image, np.ones((yscale, xscale), np.uint8), iterations=1)
    _, thresh_img = cv2.threshold(thresh_img, 250, 255, cv2.THRESH_BINARY)
    return thresh_img


def black_points_count(image: np.ndarray, axis: int):
    count = np.vectorize(lambda s: image.shape[axis] - int(s / 255))
    return count(np.sum(image, axis=axis))


def extract_lines(original_image: np.ndarray) -> list:
    gray_image = image_preparation(original_image, 2, 1)
    count_y = black_points_count(gray_image, 1)
    extremum_lines = [extr for extr in argrelextrema(count_y, np.less_equal, order=2)[0] if count_y[extr] <= 20]
    text_lines = []
    prev_line = 0
    for line in extremum_lines:
        if prev_line + 1 < line:
            text_lines.append(original_image[prev_line:line, ])
        prev_line = line
    if prev_line != original_image.shape[0] - 1:
        text_lines.append(original_image[prev_line:original_image.shape[0] - 1, ])
    return text_lines


def extract_words(line: np.ndarray) -> list:
    count_x = black_points_count(image_preparation(line, 3, 1), 0)
    spaces = [extr for extr in argrelextrema(count_x, np.less_equal, order=2)[0] if count_x[extr] == 0]
    if len(spaces) == 0:
        return []
    words = [] if spaces[0] == 0 else [line[:, 0:spaces[0]]]
    prev_space = 0
    for space in spaces:
        if prev_space + 1 < space:
            words.append(line[:, prev_space:space])
        prev_space = space
    return words


def extract_letters(word: np.ndarray) -> list:
    count_x = black_points_count(image_preparation(word, 1, 3), 0)
    spaces = [extr for extr in argrelextrema(count_x, np.less_equal, order=2)[0] if count_x[extr] <= 5]
    if len(spaces) == 0:
        return []
    words = [] if spaces[0] == 0 else [word[:, 0:spaces[0]]]
    prev_space = 0
    for space in spaces:
        if prev_space + 1 < space:
            words.append(word[:, prev_space:space])
        prev_space = space
    return words
