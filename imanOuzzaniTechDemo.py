# import modules

import gtts
from playsound import playsound
import pyautogui
from pynput import keyboard
from pynput.mouse import Listener
import cv2
import pytesseract
import os

# predefined coordinates of first paragraph
paragraphTopcoord = [242, 397]
paragraphBotcoord = [1052, 567]
widthOfScreenshot = 1052 - 242
heightOfScreenshot = 567 - 397


def on_press(key):
    # when alt key pressed start listening for a mouse press
    if key == keyboard.Key.alt:
        def on_click(x, y, button, pressed):
            if pressed:
                # receive mouse press coordinates
                mousePressCoord = [x, y]
            elif not pressed:
                return False

            # checks if mouse press is in the range of the first paragraph
            if paragraphTopcoord[0] < mousePressCoord[0] < paragraphBotcoord[
                0] and paragraphTopcoord[1] < mousePressCoord[1] < \
                    paragraphBotcoord[1]:
                # extract a screenshot of the first paragraph
                img = pyautogui.screenshot('catsParagraphOne.png', region=(
                    paragraphTopcoord[0], paragraphTopcoord[1],
                    widthOfScreenshot, heightOfScreenshot))

        # used to listen for the mouse presses
        with Listener(on_click=on_click) as listener:
            listener.join()
    # keyboard listening stopped with esc
    if key == keyboard.Key.esc:
        return False


# used to listen for the key presses
with keyboard.Listener(on_press=on_press) as listener:
    listener.join()

if os.path.isfile('catsParagraphOne.png'):
    # convert image from png to jpg so it can be used for the OCR
    pngToJpg = cv2.imread('catsParagraphOne.png')
    cv2.imwrite('catsParagraphOne.jpg', pngToJpg)

    # remove extra files created for screen reading process
    os.remove('catsParagraphOne.png')

    # extract string from image using OCR
    imageForOCR = cv2.imread('catsParagraphOne.jpg')
    custom_config = r'--oem 3 --psm 6'
    ttsString = pytesseract.image_to_string(imageForOCR, config=custom_config)

    # perform text to speech on extracted string
    tts = gtts.gTTS(ttsString)
    tts.save("ttsTest.mp3")
    playsound("ttsTest.mp3")

    # remove extra files created for screen reading process
    os.remove('catsParagraphOne.jpg')
    os.remove("ttsTest.mp3")
else:
    # if the catsParagraphOne.png image is not created - the coordinates pressed
    # were not correct or not registered correctly
    tts = gtts.gTTS("Please Try Again")
    tts.save("ttsTryAgain.mp3")
    playsound("ttsTryAgain.mp3")
    os.remove("ttsTryAgain.mp3")
