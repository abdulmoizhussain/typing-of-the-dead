import cv2 as cv
from mss import mss
import pyautogui
from PIL import Image
import numpy as np

sct = mss()
game_width, game_height = 640, 480  # Game's resolution
w, h = pyautogui.size()
monitor = {'top': 0, 'left': w, 'width': game_width, 'height': game_height}
window_source = "Source"
window_processed = "Processed"


def avg_of_difference(a, b, percent):
    return (a if a < b else b) + (abs(a - b) * percent)


def put_text(img, text, x, y):
    cv.putText(img,
               text,
               (x, y),
               cv.FONT_HERSHEY_SIMPLEX,
               1,
               (255, 255, 0),
               2)


def show_detections(img, contour, text, x, y):
    cv.drawContours(img, [contour], 0, [0, 0, 255], 2)
    cv.putText(img,
               text,
               (x, y),
               cv.FONT_HERSHEY_SIMPLEX,
               1,
               (255, 255, 0),
               2)
    cv.imshow(window_source, img)


def take_ss():
    return cv.cvtColor(
        np.array(Image.frombytes("RGB", (game_width, game_height), sct.grab(monitor).rgb)),
        cv.COLOR_RGB2BGR
    )


SHIFT_KEY = {
    "~": "`",
    "!": "1",
    "@": "2",
    "#": "3",
    "$": "4",
    "%": "5",
    "^": "6",
    "&": "7",
    "*": "8",
    "(": "9",
    ")": "0",
    "_": "-",
    "+": "=",
    "{": "[",
    "}": "]",
    "|": "\\",
    ":": ";",
    "\"": "'",
    "<": ",",
    ">": ".",
    "?": "/"
}


def type_it(char):
    if SHIFT_KEY.keys().__contains__(char):
        pyautogui.keyDown("shift")
        pyautogui.press(SHIFT_KEY[char])
        pyautogui.keyUp("shift")
    else:
        pyautogui.press(char)
        # pyautogui.typewrite cannot type shift-keys.
