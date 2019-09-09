# https://stackoverflow.com/questions/9426045/difference-between-exit0-and-exit1-in-python/9426115
from tkinter import Label, Entry, Tk, Button, scrolledtext, INSERT
from tkinter.ttk import Combobox
import os
from screeninfo import get_monitors
import cv2.cv2 as cv
import pytesseract
from win32api import GetKeyState
from win32con import VK_CAPITAL
from threading import Thread
from Common import \
    avg_of_difference, \
    show_contours, \
    take_ss, \
    window_source, \
    put_text, \
    type_it, \
    game_width, \
    game_height

# https://stackoverflow.com/questions/50655738/tesseractnotfounderror
pytesseract.pytesseract.tesseract_cmd = os.path.abspath("./Tesseract-OCR/tesseract.exe")

_CAPTURE = True
_STATE = {"TOP": 0,
          "LEFT": 0,
          "MIN_BOX_W": 0,
          "MIN_BOX_H": 0,
          "TYPING_DELAY": 0,
          "WAIT_KEY": 0}

connectedMonitors = get_monitors()


def _print(log_text):
    logSection.configure(state="normal")
    logSection.insert(INSERT, chars=log_text + "\n")
    logSection.configure(state="disabled")


def br():
    Label(window, text="").pack()


def start_capturing():
    global _CAPTURE, _STATE
    _CAPTURE = True
    ignition.configure(command=stop_capturing, text="STOP")
    for cm in connectedMonitors:
        if cm.name == comboboxMonitors.get():
            _STATE["TOP"] = cm.y
            _STATE["LEFT"] = cm.x
            break
    _STATE["MIN_BOX_W"] = int(entryMinBoxW.get())
    _STATE["MIN_BOX_H"] = int(entryMinBoxH.get())
    _STATE["TYPING_DELAY"] = int(entryTypingDelay.get())
    _STATE["WAIT_KEY"] = int(entryWaitKey.get())
    Thread(target=start).start()


def stop_capturing():
    global _CAPTURE
    _CAPTURE = False
    ignition.configure(command=start_capturing, text="START")


def start():
    cv.namedWindow(window_source, cv.WINDOW_NORMAL)
    cv.resizeWindow(window_source, game_width, game_height)
    monitor_config = {"top": _STATE["TOP"],
                      "left": _STATE["LEFT"],
                      "width": game_width,
                      "height": game_height}
    while True:
        img = take_ss(monitor_config)
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
            # Should be like upper line ^ But updated coordinates will be taken.
            # cv.drawContours(img, [contour], -1, [0, 0, 255], 2)
            text_box_x_start, text_box_y_start = corners[0], corners[1]
            text_box_x_end, text_box_y_end = corners[2], corners[7]
            text_box_width = text_box_x_end - text_box_x_start
            text_box_height = text_box_y_end - text_box_y_start
            if text_box_width < _STATE["MIN_BOX_W"] or text_box_height < _STATE["MIN_BOX_H"]:
                continue
            img_text_box = img[text_box_y_start:text_box_y_end, text_box_x_start:text_box_x_end]
            try:
                text = pytesseract.image_to_string(img_text_box)
            except Exception as E:
                text = ""
                _print(str(E))
            t1 = Thread(target=cv.drawContours, args=(img, [contour], 0, [255, 255, 0], 2,))
            t1.start()
            if len(text) < 1 or text.find("\n") < 0:
                continue
            text_to_type = text.split("\n")[1]
            if len(text_to_type) < 1:
                continue
            text_to_type = text_to_type \
                .replace("’", "'") \
                .replace("”", "\"") \
                .replace("|", "I")
            # .replace(" ", "") \
            # .lower()
            put_text(img, text_to_type, text_box_x_start, text_box_y_start)
            if GetKeyState(VK_CAPITAL) is 0:
                continue
            t1.join()
            _print("UNFILTERED >" + text)
            _print("FILTERED >>" + text_to_type)
            for char in text_to_type:
                t3 = Thread(target=type_it, args=(char,))
                t3.start()
                show_contours(
                    take_ss(monitor_config),
                    approx,
                    text_to_type,
                    text_box_x_start,
                    text_box_y_start
                )
                cv.waitKey(_STATE["TYPING_DELAY"])  # lower than 1 millisecond will not be functional.
                t3.join()
        cv.imshow(window_source, img)
        if cv.waitKey(_STATE["WAIT_KEY"]) & (_CAPTURE is False):
            cv.destroyAllWindows()
            break


# Starting UI development.
window = Tk()
window.title("Typing of the Dead - Auto Player")
window.geometry("640x600")

Label(window, text="Min box width:").pack()

entryMinBoxW = Entry(window, width=4)
entryMinBoxW.pack()
entryMinBoxW.insert(0, "20")
# entry_min_w.delete(0, len(entry_min_w.get()))

Label(window, text="Min box height:").pack()
entryMinBoxH = Entry(window, width=4)
entryMinBoxH.pack()
entryMinBoxH.insert(0, "30")

br()

Label(window, text="Key press delay i.e typing speed (in milli-seconds) "
                   "(must not be smaller than 1):").pack()
entryTypingDelay = Entry(window, width=4)
entryTypingDelay.pack()
entryTypingDelay.insert(0, "1")

br()

Label(window, text="Recording speed "
                   "(after how many milli-seconds one frame will be take)"
      ).pack()
entryWaitKey = Entry(window, width=4)
entryWaitKey.pack()
entryWaitKey.insert(0, "20")

br()

Label(window, text="Select monitor on which game will run:").pack()

comboboxMonitors = Combobox(window)
comboboxMonitors["values"] = [monitor.name for monitor in connectedMonitors]
comboboxMonitors.pack()
comboboxMonitors.current(0)

ignition = Button(window, text="START")
ignition.configure(command=start_capturing)
ignition.pack()

Label(window, text="!! NOTE !!").pack()
Label(window, text="When CAPS_LOCK is off, it will only detect the words.").pack()
Label(window, text="When CAPS_LOCK is on, it will type.").pack()

br()
Label(window, text="!! IMPORTANT !!").pack()

Label(window, text="Disable or close application(s), which have any option like this,").pack()
Label(window, text="\"MOVE MOUSE TO A CORNER OF SCREEN WHILE TYPING\".").pack()

logSection = scrolledtext.ScrolledText(window)
logSection.configure(state="disabled")
logSection.pack()

window.mainloop()
