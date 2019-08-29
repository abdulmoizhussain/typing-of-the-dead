# https://stackoverflow.com/questions/9426045/difference-between-exit0-and-exit1-in-python/9426115
import cv2 as cv
import pytesseract
from win32api import GetKeyState
from win32con import VK_CAPITAL
from threading import Thread
from Common import \
    avg_of_difference, \
    show_detections, \
    take_ss, \
    window_source, \
    put_text, \
    type_it

# https://stackoverflow.com/questions/50655738/tesseractnotfounderror
pytesseract.pytesseract.tesseract_cmd = r"C:\Program Files\Tesseract-OCR\tesseract.exe"

# print(GetMonitorInfo(MonitorFromPoint((0, 0))))
# exit(0)

cv.namedWindow(window_source, cv.WINDOW_NORMAL)
cv.resizeWindow(window_source, 640, 480)
while True:
    img = take_ss()
    gray = cv.cvtColor(img, cv.COLOR_BGR2GRAY)
    _, threshold = cv.threshold(gray, 125, 125, cv.THRESH_BINARY)
    contours, hierarchy = cv.findContours(threshold, cv.RETR_TREE, cv.CHAIN_APPROX_NONE)
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
        text_box_x_start, text_box_y_start = corners[0], corners[1]
        text_box_x_end, text_box_y_end = corners[2], corners[7]
        text_box_width = text_box_x_end - text_box_x_start
        text_box_height = text_box_y_end - text_box_y_start
        if text_box_width < 20 or text_box_height < 30:
            continue
        img_text_box = \
            img[text_box_y_start:text_box_y_end, text_box_x_start:text_box_x_end]
        try:
            text = pytesseract.image_to_string(img_text_box)
        except Exception as E:
            text = ""
            print(E)
        t1 = Thread(target=cv.drawContours, args=(img, [contour], 0, [255, 255, 0], 2,))
        t1.start()
        if len(text) < 1 or text.find("\n") < 0:
            continue
        text_to_type = text.split("\n")[1]
        if len(text_to_type) < 1:
            continue
        text_to_type = text_to_type \
            .replace("’", "'") \
            .replace("”", '"') \
            .replace("|", "I")
        # .replace(" ", "") \
        # .lower()
        put_text(img, text_to_type, text_box_x_start, text_box_y_start)
        if GetKeyState(VK_CAPITAL) is 0:
            continue
        t1.join()
        print(">" + text)
        print(">>" + text_to_type)
        for char in text_to_type:
            t3 = Thread(target=type_it, args=(char,))
            t3.start()
            show_detections(
                take_ss(),
                approx,
                text_to_type,
                text_box_x_start,
                text_box_y_start
            )
            cv.waitKey(1)  # lower than 1 millisecond will not be functional.
            t3.join()
    cv.imshow(window_source, img)
    if cv.waitKey(20) & 0xFF == ord("q"):
        cv.destroyAllWindows()
        break
