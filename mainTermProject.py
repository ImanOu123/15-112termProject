import gtts
from playsound import playsound
import pyautogui
from pynput import keyboard
from pynput.mouse import Listener, Controller
import cv2
import pytesseract
import os
from cmu_112_graphics import *
from pytesseract import Output


def distinguishSections(img):
    # perform OCR on screenshot of full page
    custom_config = r'--oem 3 --psm 1'
    string = pytesseract.image_to_string(img, config=custom_config)

    sectionsLst = string.split("\n\n")
    cleanSectionLst = []

    # create a new list of words separated by section
    for i in sectionsLst:
        cleanSectionLst.append(i.replace("\n", " ").split(" "))

    # remove any unnecessary characters
    for i in range(len(cleanSectionLst)):
        if " " in cleanSectionLst[i]:
            cleanSectionLst[i] = list(filter(" ".__ne__, cleanSectionLst[i]))
        if "" in cleanSectionLst[i]:
            cleanSectionLst[i] = list(filter("".__ne__, cleanSectionLst[i]))

    if [] in cleanSectionLst:
        cleanSectionLst.remove([])

    # extra relevant data about the words on the image - coordinates
    dataDict = pytesseract.image_to_data(img, output_type=Output.DICT,
                                         config=custom_config)
    lstWords = list(dataDict["text"])

    def betterIdx(lst, word, num):
        # extracts the nth duplicate's index
        counter = 0
        lastIdx = 0
        for i in range(len(lst)):
            if lst[i] == word:
                counter += 1
                lastIdx = i
            if counter == num:
                return i
        return lastIdx

    # split each section with associated indices
    idxDict = {}
    dupWords = {}

    # links each section to the indices of the words in that section
    for i in cleanSectionLst:
        val = []
        for word in i:
            if word in lstWords:
                val.append(betterIdx(lstWords, word, dupWords.get(word, 1)))
            # to avoid issues with duplicates
            dupWords[word] = dupWords.get(word, 1) + 1
        idxDict[" ".join(i)] = val

    # extracts coordinates of each word in section
    coordDict = {}
    for key in idxDict:
        coordDict[key] = []
        for val in idxDict[key]:
            coordDict[key].append([dataDict["left"][val], dataDict["top"][val],
                                   dataDict["width"][val],
                                   dataDict["height"][val]])

    # find min and max coord of coordinates of words to get overall coordinates
    # for the whole section

    minMaxCoord = {}

    for elem in coordDict:
        minMaxCoord[elem] = [99999, 99999, 0, 0]
        for i in coordDict[elem]:
            # print(i[0], i[1], minMaxCoord[elem])
            if i[0] <= minMaxCoord[elem][0]:
                minMaxCoord[elem][0] = i[0]

            if i[0] + i[2] >= minMaxCoord[elem][2]:
                minMaxCoord[elem][2] = i[0] + i[2]

            if i[1] <= minMaxCoord[elem][1]:
                minMaxCoord[elem][1] = i[1]

            if i[1] + i[3] >= minMaxCoord[elem][3]:
                minMaxCoord[elem][3] = i[1] + i[3]

    # remove extra files created for screen reading process
    os.remove('fullPgScreenshot.png')

    return minMaxCoord



def mouseClickDetections(stringWCoordDict, runListener):
    def on_click(x, y, button, pressed):
        mousePressCoord = [0, 0]
        # if runListener is False then stop the program
        if not runListener:
            return False
        if pressed:
            # receive mouse press coordinates
            mousePressCoord = [x, y]
        # check if if the mousePress is within any of the predefined sections
        for string in stringWCoordDict:
            if stringWCoordDict[string][0] <= mousePressCoord[0] <= stringWCoordDict[string][2] and \
                    stringWCoordDict[string][1] < mousePressCoord[1] < stringWCoordDict[string][3]:
                # perform text to speech on extracted string
                tts = gtts.gTTS(string)
                tts.save("ttsOnString.mp3")
                playsound("ttsOnString.mp3")

                # remove extra files created for screen reading process
                os.remove('ttsOnString.mp3')

    with Listener(on_click=on_click) as listener:
        listener.join()


def userInterface():
    # in order to run the program, the user must press alt
    def on_press(key):
        # preliminary variables
        runListener = False
        stringWCoordDict = {}

        # when alt key pressed start listening for a mouse press
        if key == keyboard.Key.alt:
            # moves mouse to the top left of the page
            mouse = Controller()
            mouse.position = (0, 1080)
            tts = gtts.gTTS("The mouse has been moved to the bottom left of the page")
            tts.save("mouseMove.mp3")
            playsound("mouseMove.mp3")
            os.remove("mouseMove.mp3")
            runListener = True

            # takes a screenshot of the current page
            img = pyautogui.screenshot('fullPgScreenshot.png', region=(0, 0, 2560, 1600))

            # convert image from png to jpg so it can be used for the OCR
            pngToJpg = cv2.imread('fullPgScreenshot.png')
            cv2.imwrite('fullPgScreenshot.jpg', pngToJpg)

            # extract sections of webpage
            stringWCoordDict = distinguishSections(img)

            # When the page is prepared for TTS
            tts = gtts.gTTS("You may now begin clicking")
            tts.save("prepClicking.mp3")
            playsound("prepClicking.mp3")
            os.remove("prepClicking.mp3")

            # check whether the mouse clicks are in any sections
            mouseClickDetections(stringWCoordDict, runListener)

        # keyboard listening stopped with esc
        elif key == keyboard.Key.esc:
            runListener = False
            # stops mouse listener
            mouseClickDetections(stringWCoordDict, runListener)
            return False

    # used to listen for the key presses
    with keyboard.Listener(on_press=on_press) as listener:
        listener.join()


userInterface()
