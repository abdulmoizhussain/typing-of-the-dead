# https://stackoverflow.com/questions/9426045/difference-between-exit0-and-exit1-in-python/9426115
import cv2 as cv
import pyautogui
import pytesseract
from win32api import GetKeyState
from win32con import VK_CAPITAL

from Common import \
    avg_of_difference, \
    show_detections, \
    game_width, \
    game_height, \
    take_ss, \
    window_source, \
    window_processed, \
    put_text

running = True
# https://stackoverflow.com/questions/50655738/tesseractnotfounderror
pytesseract.pytesseract.tesseract_cmd = r"C:\Program Files\Tesseract-OCR\tesseract.exe"

# print(GetMonitorInfo(MonitorFromPoint((0, 0))))
# exit(0)

# pyautogui.hotkey('shift', '`')
# pyautogui.keyDown("shift")
# pyautogui.press('/')
# pyautogui.keyUp("shift")

# exit(0)

# pyautogui.typewrite('Hello world!', interval=0.08)
# # pyautogui.sleep(2)
# print ("asdasd")

# cv.namedWindow(window_processed, cv.WINDOW_NORMAL)
# cv.resizeWindow(window_processed, 640, 480)
cv.namedWindow(window_source, cv.WINDOW_NORMAL)
cv.resizeWindow(window_source, 640, 480)
while True:
    img = take_ss()
    gray = cv.cvtColor(img, cv.COLOR_BGR2GRAY)
    _, threshold = cv.threshold(gray, 125, 125, cv.THRESH_BINARY)
    contours, hierarchy = cv.findContours(threshold, cv.RETR_TREE, cv.CHAIN_APPROX_NONE)
    try:
        for contour in contours:
            approx = cv.approxPolyDP(contour, 0.03 * cv.arcLength(contour, True), True)
            if len(approx) != 4:
                continue
            corners = approx.ravel()
            c1x, c1y = corners[0], corners[1]
            c2x, c2y = corners[2], corners[3]
            c3x, c3y = corners[4], corners[5]
            c4x, c4y = corners[6], corners[7]
            #   c1                        c2
            #     _______________________
            #    |                       |
            #    |                       |
            #    |_______________________|
            #  c4                         c3
            
            # y-average
            corners[1] = corners[3] = (c1y + c2y) / 2
            corners[5] = corners[7] = avg_of_difference(c3y, c4y, 0.85)  # 80%
            
            # x-average
            corners[0] = corners[6] = c1x if c1x > c4x else c4x
            corners[2] = corners[4] = (c2x + c3x) / 2
            
            # cropped_img = img[y:y + h, x:x + w] # Example
            # cropped_img = img[c1y:(c4y - c1y), c1x:(c2x - c1x)]
            # Should be like upper line ^ but updated coordinates will be taken.
            # cv.drawContours(img, [contour], -1, [0, 0, 255], 2)
            text_box_x, text_box_y = corners[0], corners[1]
            text_box_width = corners[2]
            text_box_height = corners[7]
            if text_box_width - text_box_x < 20 or text_box_height - text_box_y < 20:
                continue
            img_text_box = img[text_box_y:text_box_height, text_box_x:text_box_width]
            text = pytesseract.image_to_string(img_text_box)
            cv.drawContours(img, [contour], 0, [255, 255, 0], 2)
            if len(text) < 1 or text.find("\n") < 0:
                continue
            text_to_type = text.split("\n")[1]
            if len(text_to_type) < 1:
                continue
            # cv.imshow(window_processed, img_text_box)
            text_to_type = text_to_type \
                .replace("’", "'") \
                .replace("”", '"') \
                .replace("|", "I")
            # .replace(" ", "") \
            # .lower()
            put_text(img, text_to_type, text_box_x, text_box_y)
            if GetKeyState(VK_CAPITAL) is 0:
                continue
            print("__" + text)
            print(text_to_type)
            for letter in text_to_type:
                show_detections(
                    take_ss(),
                    approx,
                    text_to_type,
                    text_box_x,
                    text_box_y
                )
                if letter == "!":
                    pyautogui.keyDown("shift")
                    pyautogui.press('1')
                    pyautogui.keyUp("shift")
                elif letter == "?":
                    pyautogui.keyDown("shift")
                    pyautogui.press('/')
                    pyautogui.keyUp("shift")
                else:
                    pyautogui.press(letter)
                cv.waitKey(0.5)
                # time.sleep(0.001)
            # pyautogui.typewrite(text_to_type, interval=0.08)
    except Exception as E:
        if E is True:
            print(E)
    cv.imshow(window_source, img)
    if cv.waitKey(20) & 0xFF == ord("q"):
        cv.destroyAllWindows()
        break
