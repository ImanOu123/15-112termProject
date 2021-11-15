import gtts
from playsound import playsound
import pyautogui
from pynput import keyboard
from pynput.mouse import Listener, Controller
import cv2
import pytesseract
import os
import basic_graphics
from cmu_112_graphics import *

# websites to test project on
#   https://en.wikipedia.org/wiki/Cat
#   https://www.thenation.com/left-behind/
#   need websites with column paragraphs

def distinguishSections(screenWidth, screenHeight):
    # screenshot of full screen
    # if scroll detected, new screenshot
    # divide each section by coordinates
    # sectionCoord is a list of a set coordinates of top and bottom of each
    # section
    # make sure coordinates don't overlap
    sectionCoord = [(0, 0, 10, 10), (20, 20, 30, 30)]
    return sectionCoord


def screenshotandOCRSections(sectionCoord):
    coordWStringsDict = {}
    for coord in sectionCoord:
        # takes a screenshot of section
        screenshotSection = pyautogui.screenshot('ocrForImage.png',
                                                 region=coord)

        # convert image from png to jpg so it can be used for the OCR
        pngToJpg = cv2.imread('ocrForImage.png')
        cv2.imwrite('ocrForImage.jpg', pngToJpg)

        # remove extra files created for screen reading process
        os.remove('ocrForImage.png')

        # extract string from image using OCR
        imageForOCR = cv2.imread('ocrForImage.jpg')
        custom_config = r'--oem 3 --psm 6'
        ttsString = pytesseract.image_to_string(imageForOCR,
                                                config=custom_config)
        # store string in dictionary to be used for later tts
        coordWStringsDict[coord] = ttsString

        # remove extra files created for screen reading process
        os.remove('ocrForImage.jpg')

    return coordWStringsDict


def mouseClickDetections(coordWStringDict, runListener):
    def on_click(x, y, button, pressed):
        mousePressCoord = [0, 0]
        # if runListener is False then stop the program
        if not runListener:
            return False
        if pressed:
            # receive mouse press coordinates
            mousePressCoord = [x, y]
        # check if if the mousePress is within any of the predefined sections
        for coord in coordWStringDict:
            if coord[0] < mousePressCoord[0] < coord[2] and coord[1] < \
                    mousePressCoord[1] < coord[3]:
                # perform text to speech on extracted string
                tts = gtts.gTTS(coordWStringDict[coord])
                tts.save("ttsOnString.mp3")
                playsound("ttsOnString.mp3")

                # remove extra files created for screen reading process
                os.remove('ttsOnString.mp3')
            else:
                # ask user to click on an acceptable section
                tts = gtts.gTTS("Please click on an acceptable section.")
                tts.save("ttsAccept.mp3")
                playsound("ttsAccept.mp3")

                # remove extra files created for screen reading process
                os.remove('ttsAccept.mp3')

    with Listener(on_click=on_click) as listener:
        listener.join()


def main():
    def draw(canvas, width, height, message, color):
        # GUI for application

        def appStarted(app):
            app.counter = 0

        def keyPressed(app, event):
            app.counter += 1

        def redrawAll(app, canvas):
            canvas.create_text(app.width / 2, app.height / 2,
                               text=f'{app.counter} keypresses',
                               font='Arial 30 bold')

    runApp(width=400, height=400)

    # in order to run the program, the user must press alt
    def on_press(key):
        # moves mouse to the top left of the page
        mouse = Controller()
        mouse.position = (0, 0)
        tts = gtts.gTTS("The mouse has been moved to the top left of the page")
        tts.save("mouseMove.mp3")
        playsound("mouseMove.mp3")
        os.remove("mouseMove.mp3")

        # preliminary variables
        runListener = False
        coordWStringDict = {}

        # when alt key pressed start listening for a mouse press
        if key == keyboard.Key.alt:
            runListener = True
            # keyboard listening stopped with esc
        elif key == keyboard.Key.esc:
            runListener = False
            return False

        if runListener:
            sectionCoord = distinguishSections(1920, 1080)
            coordWStringsDict = screenshotandOCRSections(sectionCoord)
        mouseClickDetections(coordWStringsDict, runListener)

    # used to listen for the key presses
    with keyboard.Listener(on_press=on_press) as listener:
        listener.join()
