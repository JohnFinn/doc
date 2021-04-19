import cv2
import numpy as np
from matplotlib import pyplot as plt
from matplotlib.pyplot import figure
# from scipy.signal import savgol_filter


def box_around_letter_open_cv():
    image_file = 'test.png'
    img = cv2.imread(image_file)
    gray = cv2.cvtColor(img, cv2.COLOR_BGR2GRAY)
    ret, thresh = cv2.threshold(gray, 127, 255, cv2.THRESH_BINARY)
    img_erode = cv2.erode(thresh, np.ones((2, 2), np.uint8), iterations=1)

    contours, hierarchy = cv2.findContours(img_erode, cv2.RETR_TREE, cv2.CHAIN_APPROX_NONE)
    output = img_erode.copy()

    contours.sort(key=lambda c1: cv2.boundingRect(c1)[0])
    for idx, contour in enumerate(contours):
        (x, y, w, h) = cv2.boundingRect(contour)
        letter_img = output[y:y + h, x:x + w]
        cv2.imwrite('result_words/' + str(idx) + '.png', letter_img)
        cv2.rectangle(output, (x, y), (x + w, y + h), (1, 0, 0), 1)

    cv2.imwrite('output.png', output)
    # cv2.imwrite('../erode.png', img_erode)


def box_around_letter_histogram():
    figure(figsize=(20, 6))
    gray = cv2.cvtColor(cv2.imread('test.png'), cv2.COLOR_BGR2GRAY)
    _, thresh_img = cv2.threshold(gray, 50, 255, cv2.THRESH_BINARY)
    thresh_img = cv2.erode(thresh_img, np.ones((1, 1), np.uint8), iterations=1)
    plt.imshow(thresh_img, 'gray', vmin=0, vmax=255)
    v_black_count_x = np.vectorize(lambda s: int(s / 255))
    v_black_count_y = np.vectorize(lambda s: thresh_img.shape[1] - int(s / 255))
    counts_y = v_black_count_y(np.sum(thresh_img, axis=1))
    white_lines = list(np.where(counts_y == 0)[0])
    images_lines = [] if white_lines[0] == 0 else [thresh_img[0:white_lines[0]]]
    for i in range(len(white_lines) - 1):
        if white_lines[i] + 1 == white_lines[i + 1]:
            continue
        images_lines.append(thresh_img[white_lines[i]:white_lines[i + 1], ])
        cv2.imwrite('result_lines/' + str(i) + '.png', images_lines[len(images_lines) - 1])
    for i, line in enumerate(images_lines):
        counts_x = v_black_count_x(np.sum(line, axis=0))
        spaces = list(np.where(counts_x == line.shape[0])[0])
        if len(spaces) == 0:
            continue
        letters = [] if spaces[0] == 0 else [line[:, 0:spaces[0]]]
        for j in range(len(spaces) - 1):
            if spaces[j] + 1 == spaces[j + 1]:
                continue
            letters.append(line[:, spaces[j]:spaces[j + 1]])
        for j, letter in enumerate(letters):
            cv2.imwrite('result_letters/' + str(i) + '_' + str(j) + '.png', letter)

    # plt.show()
