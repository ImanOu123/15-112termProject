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
    # take a screenshot of the page
    # use ocr on the page
    # find new paragraphs based on spaces in string
    # find locations of first word and word farthest to the left through
    # text localization

    img = pyautogui.screenshot('fullPgScreenshot.png',
                               region=(0, 0, screenWidth, screenHeight))

    # convert image from png to jpg so it can be used for the OCR
    pngToJpg = cv2.imread('fullPgScreenshot.png')
    cv2.imwrite('realTimeSample.jpg', pngToJpg)

    # remove extra files created for screen reading process
    os.remove('fullPgScreenshot.png')

    # extract string from image using OCR
    imageForOCR = cv2.imread('realTimeSample.jpg')
    custom_config = r'--oem 3 --psm 6'
    ttsString = pytesseract.image_to_string(imageForOCR,
                                            config=custom_config)

    # UNCOMMENT --> CITE THIS CODE

    # results = pytesseract.image_to_data("realTimeSample.jpg", output_type=Output.DICT)
    # # loop over each of the individual text localizations
    # for i in range(0, len(results["text"])):
    #     # extract the bounding box coordinates of the text region from
    #     # the current result
    #     x = results["left"][i]
    #     y = results["top"][i]
    #     w = results["width"][i]
    #     h = results["height"][i]
    #     # extract the OCR text itself along with the confidence of the
    #     # text localization
    #     text = results["text"][i]
    #     conf = int(results["conf"][i])
    #
    #     print(text, x, y, w, h)

    def on_scroll(x, y, button, pressed):
        pass
        # if scroll detected take a new screen shot

    with Listener(on_scroll=on_scroll) as listener:
        listener.join()

    sectionCoord = [(0, 0, 10, 10), (20, 20, 30, 30)]
    return sectionCoord


def screenshotandOCRSections(sectionCoord):  # remove if OCR text localization
    # works
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
    # in order to run the program, the user must press alt
    def on_press(key):
        # preliminary variables
        runListener = False
        coordWStringsDict = {}

        # when alt key pressed start listening for a mouse press
        if key == keyboard.Key.alt:
            # moves mouse to the top left of the page
            mouse = Controller()
            mouse.position = (0, 0)
            tts = gtts.gTTS(
                "The mouse has been moved to the top left of the page")
            tts.save("mouseMove.mp3")
            playsound("mouseMove.mp3")
            os.remove("mouseMove.mp3")
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


# GUI for application

def appStarted(app):
    tts = gtts.gTTS("Press the space bar to listen to the instructions")
    tts.save("startSpeech.mp3")
    playsound("startSpeech.mp3")
    os.remove("startSpeech.mp3")

    app.instructions = """This application is a screen reader that helps you 
                    navigate websites. In order to use this screen reader 
                    go to the webpage that you want to be read and press alt. 
                    When you press alt your mouse will be moved to the top left
                    of the page. In order to stop the program press esc. 
                    You can now begin to use the screen reader. In order to 
                    repeat the instructions press space, to leave the instructions 
                    page press l"""


def keyPressed(app, event):
    # if the user presses space the instructions are read out
    if event.key == "Space":
        tts = gtts.gTTS(app.instructions)
        tts.save("instructionsSpeech.mp3")
        playsound("instructionsSpeech.mp3")
        os.remove("instructionsSpeech.mp3")

    if event.key == "l":
        pass
        # leave application


def redrawAll(app, canvas):
    canvas.create_text(app.width / 2, app.height / 2, text=
    """This application is a screen reader that helps you 
    navigate websites. In order to use this screen reader 
    go to the webpage that you want to be read and press alt. 
    When you press alt your mouse will be moved to the top left
    of the page. In order to stop the program press esc. 
    You can now begin to use the screen reader. In order to 
    repeat the instructions press space, to leave the instructions 
    page press L""")


runApp(width=400, height=400)

main()
