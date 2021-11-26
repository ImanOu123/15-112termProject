import gtts
from playsound import playsound
import pyautogui
from pynput import keyboard
from pynput import mouse
from pynput.mouse import Controller
import cv2
import pytesseract
from cmu_112_graphics import *
from pytesseract import Output
from mainTermProjectArPOSTMVP import *

# Post-MVP Modules
from imageai.Detection import ObjectDetection
from googletrans import Translator, constants


# GITHUB REPO - https://github.com/ImanOu123/15-112termProject

def distinguishSections(img):
    # perform OCR on screenshot of full page

    custom_config = r'--oem 3 --psm 1'
    string = pytesseract.image_to_string(img, config=custom_config)

    # splits each section based on the new lines within the strings

    sectionsLst = string.split("\n\n")
    cleanSectionLst = []

    # create a new list of words separated by section

    for i in sectionsLst:
        cleanSectionLst.append(i.replace("\n", " ").split(" "))

    # remove any unnecessary characters such as empty quotes

    for i in range(len(cleanSectionLst)):
        if " " in cleanSectionLst[i]:
            cleanSectionLst[i] = list(filter(" ".__ne__, cleanSectionLst[i]))
        if "" in cleanSectionLst[i]:
            cleanSectionLst[i] = list(filter("".__ne__, cleanSectionLst[i]))

    # removes any sections with no words to prevent issues with

    if [] in cleanSectionLst:
        cleanSectionLst.remove([])

    # extra relevant data about the words on the image - coordinates

    dataDict = pytesseract.image_to_data(img, output_type=Output.DICT,
                                         config=custom_config)
    lstWords = list(dataDict["text"])

    # helper function to help extract index of duplicated words

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

    # combine smaller sections into bigger sections to make clicking easier

    smallSections = []

    # find small sections based on section size

    for text in minMaxCoord:
        sectionSize = abs(minMaxCoord[text][2] - minMaxCoord[text][0]) * abs(
            minMaxCoord[text][3] - minMaxCoord[text][1])
        if sectionSize < 20000:
            smallSections.append(text)

    combinedTexts = []
    newMinMaxCoord = {}

    # helper function to combine the texts in the sections and their coordinates

    def combineSections(minMaxDict, text1, text2):
        combineText = text1 + " " + text2
        combineCoord = [min(minMaxDict[text1][0], minMaxDict[text2][0]),
                        min(minMaxDict[text1][1], minMaxDict[text2][1]),
                        max(minMaxDict[text1][2], minMaxDict[text2][2]),
                        max(minMaxDict[text1][3], minMaxDict[text2][3])]
        return combineText, combineCoord

    # for each small sections find small section next to it

    for text in smallSections:
        topX = minMaxCoord[text][0]
        topY = minMaxCoord[text][1]
        botX = minMaxCoord[text][2]
        botY = minMaxCoord[text][3]
        marginY = 20
        marginX = 40
        if text not in combinedTexts:
            remainList = smallSections[:smallSections.index(text)] + smallSections[smallSections.index(text) + 1:]
            for elem in remainList:
                if elem not in combinedTexts:
                    # if small sections detected close to it combine the two sections
                    if (topY - marginY < minMaxCoord[elem][3] < topY or botY < minMaxCoord[elem][
                        1] < botY + marginY) and \
                            (topX - marginX < minMaxCoord[elem][0] < topX or botX < minMaxCoord[elem][
                                2] < botX + marginX):
                        newText, newCoord = combineSections(minMaxCoord, text, elem)
                        combinedTexts += [text, elem]
                        # create a new dictionary with the bigger sections
                        newMinMaxCoord[newText] = newCoord

    # for small sections that weren't combined and sections that weren't small, add to new dictionary
    for i in minMaxCoord:
        if i not in smallSections or (i in smallSections and i not in combinedTexts):
            newMinMaxCoord[i] = [minMaxCoord[i][0], minMaxCoord[i][1], minMaxCoord[i][2], minMaxCoord[i][3]]

    return newMinMaxCoord


# BUG FIX - CHECKING URL TO CHECK IF HYPERLINK PRESSED

def checkForHyperlinkPress():
    # check if page changed based on if url changed

    compareImg = pyautogui.screenshot('urlScreenshotCompare.png', region=(100, 50, 1000, 51))

    pngToJpgOG = cv2.imread('urlScreenshotOG.png')
    pngToJpgCompare = cv2.imread('urlScreenshotCompare.png')

    invertOG = cv2.bitwise_not(pngToJpgOG)
    invertCompare = cv2.bitwise_not(pngToJpgCompare)

    cv2.imwrite('urlScreenshotOG.jpg', invertOG)
    cv2.imwrite('urlScreenshotCompare.jpg', invertCompare)

    stringOG = pytesseract.image_to_string(invertOG)
    stringCompare = pytesseract.image_to_string(invertCompare)

    os.remove('urlScreenshotCompare.png')
    os.remove('urlScreenshotCompare.jpg')

    # extract urls from the string extracted via OCR - based on slash

    for word in stringOG.split(" "):
        if "/" in word or ".com" in word or ".org" in word:
            OGUrl = word

    for word in stringCompare.split(" "):
        if "/" in word or ".com" in word or ".org" in word:
            CompareUrl = word

    # checks if urls are equal to detect whether a hyperlink has been clicked

    if OGUrl != CompareUrl:
        return False
    else:
        return True


# NEW FEATURE - if the user is currently hovering over a hyperlink, the program will let them know
# This detection occurs only after user requests screen reading of section

def hoveringOverHyperlink():
    # Note - has a less than 50 percent accuracy rate

    urlImg = pyautogui.screenshot('tinyURLInCorner.png', region=(0, 870, 720, 900))

    pngToJpg = cv2.imread('tinyURLInCorner.png')

    cv2.imwrite('tinyURLInCorner.jpg', pngToJpg)

    os.remove('tinyURLInCorner.jpg')
    os.remove('tinyURLInCorner.png')

    # checks whether a tiny url shows up at the bottom left of the page that indicates the user
    # is hovering of a url
    tinyURL = pytesseract.image_to_string(pngToJpg)

    if "/" in tinyURL:
        return [True, tinyURL]
    else:
        return [False]


# NEW FEATURE - detects images on the webpage and determines their location

def detectingImgsOnWebpage(imgPath):
    # Note - works based on accuracy of pretrained model

    # BUG FIX - for tensor flow error
    # (GTS, StackOverFlow, 2021)
    # https://stackoverflow.com/questions/66092421/how-to-rebuild-tensorflow-with-the-compiler-flags
    os.environ['TF_CPP_MIN_LOG_LEVEL'] = '2'

    # Using a pretrained model to detect the location of an image

    # (Priyal, Medium, 2020)
    # https://medium.datadriveninvestor.com/ai-object-detection-using-only-10-lines-of-code-imageai-89d3ba9886ea
    #
    # DOWNLOAD PREDEFINED MODEL FROM HERE - https://github.com/priyalwalpita/ai_object_detection

    execution_path = os.getcwd()
    detector = ObjectDetection()
    detector.setModelTypeAsRetinaNet()
    detector.setModelPath(os.path.join(execution_path, "resnet50_coco_best_v2.1.0.h5"))
    detector.loadModel()
    detections = detector.detectObjectsFromImage(input_image=os.path.join(execution_path, imgPath),
                                                 output_image_path=os.path.join(execution_path, "imagenew.jpg"))

    # determine all image locations and what objects are in the image
    imgLocs = {}
    for (detect, idx) in zip(detections, range(len(detections))):
        # deals with the same object found in different locations
        if detect['name'] in imgLocs:
            imgLocs[detect['name'] + str(idx)] = detect['box_points']
        else:
            imgLocs[detect['name']] = detect['box_points']

    # to avoid repetition of already combined objects

    combinedImgsCheck = []
    combinedImgsNestLst = []

    # find images that contain more than one object, based on distance or overlap of bounding box

    for (obj1, idx) in zip(imgLocs, range(len(imgLocs))):

        similarCoord = [obj1]

        for (obj2, idx2) in zip(imgLocs, range(len(imgLocs))):

            if obj2 not in similarCoord and obj2 not in combinedImgsCheck:

                # extract coordinates from dictionary

                [img1XStart, img1YStart, img1XEnd, img1YEnd] = imgLocs[obj1]
                [img2XStart, img2YStart, img2XEnd, img2YEnd] = imgLocs[obj2]

                # 2 SCENARIOS - check if bounding boxes of objects overlap or are close to one another

                # 1 - overlap

                if ((img1XStart <= img2XStart <= img1XEnd) or (img1XStart <= img2XEnd <= img1XEnd)) and \
                        (img1YStart <= img2YStart <= img1YEnd) or (img1YStart <= img2YEnd <= img1YEnd):
                    similarCoord.append(obj2)

                # 2 - close to each other

                elif ((img1XEnd <= img2XStart <= img1XEnd + 10) or (img1XStart - 10 <= img2XEnd <= img1XStart)) and \
                        ((img1YEnd <= img2YStart <= img1YEnd + 10) or (img1YStart - 10 <= img2YEnd <= img1YStart)):
                    similarCoord.append(obj2)

        # combine into a list of combined images

        if len(similarCoord) > 1:
            combinedImgsNestLst.append(similarCoord)
            combinedImgsCheck += similarCoord

    #  if multiple objects are found in an image; combine their locations and text into a user-friendly manner

    newImgLocs = {}
    for imgName in imgLocs:
        if imgName not in combinedImgsCheck:
            newImgLocs[imgName] = imgLocs[imgName]
        else:
            for combinedImgLst in combinedImgsNestLst:
                combinedName = " ".join(combinedImgLst)
                allCoord = [[], [], [], []]

                # combine the coordinates of all objects that overlap or close to each other to make one bigger object
                for combinedImgName in combinedImgLst:
                    allCoord[0].append(imgLocs[combinedImgName][0])
                    allCoord[1].append(imgLocs[combinedImgName][1])
                    allCoord[2].append(imgLocs[combinedImgName][2])
                    allCoord[3].append(imgLocs[combinedImgName][3])

                # combine the coordinates
                combinedCoord = [min(allCoord[0]), min(allCoord[1]), max(allCoord[2]), max(allCoord[3])]

                newImgLocs[combinedName] = combinedCoord

    # change text to be user friendly with use in text to speech
    finalImgLocs = {}

    for name in newImgLocs:
        nameLst = name.split(" ")
        if len(nameLst) > 1:
            firstPtLst = " ".join(nameLst[:-1])
            secondPtLst = nameLst[-1]
            finalImgLocs[f"You are hovering over an image that contains {firstPtLst} and {secondPtLst}"] = newImgLocs[
                name]
        else:
            finalImgLocs[f"You are hovering over an image that contains {nameLst[0]}"] = newImgLocs[name]

    os.remove("imagenew.jpg")
    return finalImgLocs


def mouseClickDetections():
    # for translation
    mouseClickDetections.currentlyTranslating = False
    mouseClickDetections.translateNextSec = False
    mouseClickDetections.translateLang = "en"
    mouseClickDetections.langIdx = 0

    # in order to run the program, the user must press alt

    def on_press(key):

        on_press.pgChange = False
        try:
            # NEW FEATURE - translation of next selected section
            if key.char == "t":
                tts = gtts.gTTS("You have opted to translate the next section spoken. In order to select a language to"
                                "translate to, press the w key and then press enter when you find your desired"
                                "language.", lang=userInterface.lang,
                                tld=userInterface.tld)
                tts.save("translateInstruc.mp3")
                playsound("translateInstruc.mp3")
                os.remove("translateInstruc.mp3")
                # let the user know how to use the translation

                mouseClickDetections.currentlyTranslating = True

            elif key.char == "w":
                # click up arrow key to select language
                if mouseClickDetections.currentlyTranslating:

                    # options for the language

                    langOptions = ["English", "French", "Spanish", "Arabic"]
                    mouseClickDetections.chosenLang = langOptions[mouseClickDetections.langIdx % len(langOptions)]

                    # if you want to translate to english

                    if mouseClickDetections.chosenLang == "English":
                        mouseClickDetections.translateLang = "en"
                        tts = gtts.gTTS("English", lang=userInterface.lang,
                                        tld=userInterface.tld)
                        tts.save("langChange.mp3")
                        playsound("langChange.mp3")
                        os.remove("langChange.mp3")

                    # if you want to translate to arabic

                    elif mouseClickDetections.chosenLang == "Arabic":
                        mouseClickDetections.translateLang = "ar"
                        tts = gtts.gTTS("Arabic", lang=userInterface.lang,
                                        tld=userInterface.tld)
                        tts.save("langChange.mp3")
                        playsound("langChange.mp3")
                        os.remove("langChange.mp3")

                    # if you want to translate to french

                    elif mouseClickDetections.chosenLang == "French":
                        mouseClickDetections.translateLang = "fr"
                        tts = gtts.gTTS("French", lang=userInterface.lang,
                                        tld=userInterface.tld)
                        tts.save("langChange.mp3")
                        playsound("langChange.mp3")
                        os.remove("langChange.mp3")

                    # if you want to translate to spanish

                    elif mouseClickDetections.chosenLang == "Spanish":
                        mouseClickDetections.translateLang = "es"
                        tts = gtts.gTTS("Spanish", lang=userInterface.lang,
                                        tld=userInterface.tld)
                        tts.save("langChange.mp3")
                        playsound("langChange.mp3")
                        os.remove("langChange.mp3")

                    # selection changes everytime up is pressed

                    mouseClickDetections.langIdx += 1

            elif key.char == "x":
                mouse = Controller()
                mouseClickDetections.mouseLoc = list(mouse.position)
                mouseClickDetections.mouseLoc[1] -= 100

                if not on_press.pgChange:

                    # check if if mouse is hovering within any of the predefined sections

                    for string in on_press.stringWCoordDict:

                        # NEW FEATURE - instead of clicking, the user hovers over section and presses x

                        if on_press.stringWCoordDict[string][0] <= mouseClickDetections.mouseLoc[0] <= \
                                on_press.stringWCoordDict[string][2] and \
                                on_press.stringWCoordDict[string][1] < mouseClickDetections.mouseLoc[1] < \
                                on_press.stringWCoordDict[string][3]:

                            if not mouseClickDetections.translateNextSec:
                                # perform text to speech on extracted string

                                tts = gtts.gTTS(string, lang=userInterface.lang, tld=userInterface.tld)
                                tts.save("ttsOnString.mp3")
                                playsound("ttsOnString.mp3")

                                # remove extra files created for screen reading process

                                os.remove('ttsOnString.mp3')

                            else:
                                # TRANSLATE EXTRACTED STRING
                                translator = Translator()
                                transStr = translator.translate(string, dest=mouseClickDetections.translateLang)

                                tts = gtts.gTTS(transStr.text, lang=mouseClickDetections.translateLang)
                                tts.save("ttsTransString.mp3")
                                playsound("ttsTransString.mp3")

                                # remove extra files created for screen reading process
                                os.remove('ttsTransString.mp3')

                                mouseClickDetections.translateNextSec = False

                            # check if mouse is hovering over a hyperlink

                            hovering = hoveringOverHyperlink()

                            if hovering[0]:
                                # the program will let you know that you are hovering over a hyperlink and will let
                                # you know where the hyperlink is taking you to

                                tts = gtts.gTTS(
                                    f"You are currently hovering over a hyperlink, by clicking on the link "
                                    f"you will be relocated to {hoveringOverHyperlink()[1]}",
                                    lang=userInterface.lang,
                                    tld=userInterface.tld)
                                tts.save("ttsOnString.mp3")
                                playsound("ttsOnString.mp3")

                                # remove extra files created for tts process
                                os.remove('ttsOnString.mp3')
                    on_press.pgChange = False

        except AttributeError:
            # when alt key pressed start listening for a mouse press
            if key == keyboard.Key.alt:

                # moves mouse to the top left of the page

                mouse = Controller()
                mouse.position = (0, 1080)
                tts = gtts.gTTS("The mouse has been moved to the bottom left of the page. Do not move the mouse"
                                "until the webpage has been processed", lang=userInterface.lang,
                                tld=userInterface.tld)
                tts.save("mouseMove.mp3")
                playsound("mouseMove.mp3")
                os.remove("mouseMove.mp3")

                # takes a screenshot of the current page - region doesn't include address bar -
                # may need to adjust to fit screen

                img = pyautogui.screenshot('fullPgScreenshot.png', region=(0, 100, 1440, 900))

                # use full color images for image detection on webpage

                fullColorVer = cv2.imread('fullPgScreenshot.png')
                cv2.imwrite('fullPgScreenshotfullColor.jpg', fullColorVer)

                try:
                    imgsLocs = detectingImgsOnWebpage('fullPgScreenshotfullColor.jpg')
                except:
                    imgsLocs = {}

                # for detecting whether hyperlink is pressed

                mouseClickDetections.urlImg = pyautogui.screenshot('urlScreenshotOG.png', region=(100, 50, 1000, 51))

                # convert image from png to jpg so it can be used for the OCR - Grayscale is for better recognition

                pngToJpg = cv2.imread('fullPgScreenshot.png', cv2.IMREAD_GRAYSCALE)
                cv2.imwrite('fullPgScreenshot.jpg', pngToJpg)

                # extract sections of webpage

                on_press.stringWCoordDict = distinguishSections('fullPgScreenshot.jpg')
                on_press.stringWCoordDict.update(imgsLocs)

                # When the page is prepared for TTS

                tts = gtts.gTTS("You may now begin using the screen reader", lang=userInterface.lang,
                                tld=userInterface.tld)
                tts.save("prepClicking.mp3")
                playsound("prepClicking.mp3")
                os.remove("prepClicking.mp3")

                # page change variable, won't read any text until Alt is pressed again

                on_press.pgChange = False

                # for detecting scroll

                mouseClickDetections.altPressed = True
                mouseClickDetections.scrolledCount = 0

                # for translation

                mouseClickDetections.currentlyTranslating = False
                mouseClickDetections.translateNextSec = False
                mouseClickDetections.translateLang = "en"
                mouseClickDetections.langIdx = 0

            # to leave the screen reader

            elif key == keyboard.Key.esc:

                # message when escape is pressed

                tts = gtts.gTTS("Goodbye. Thank you for using the screen reader.", lang=userInterface.lang,
                                tld=userInterface.tld)
                tts.save("goodBye.mp3")
                playsound("goodBye.mp3")
                os.remove("goodBye.mp3")

                # remove extra files

                if os.path.isfile("fullPgScreenshot.jpg"):
                    os.remove("fullPgScreenshot.jpg")
                if os.path.isfile('urlScreenshotOG.jpg'):
                    os.remove('urlScreenshotOG.jpg')
                if os.path.isfile('urlScreenshotOG.png'):
                    os.remove('urlScreenshotOG.png')
                if os.path.isfile('fullPgScreenshotfullColor.jpg'):
                    os.remove('fullPgScreenshotfullColor.jpg')

                # Stop mouse and keyboard listeners

                mListener.stop()
                return False

            # for translation

            elif key == keyboard.Key.enter:
                # language for translation is selected
                tts = gtts.gTTS(f"You have selected the language {mouseClickDetections.chosenLang}",
                                lang=userInterface.lang,
                                tld=userInterface.tld)
                tts.save("selectLang.mp3")
                playsound("selectLang.mp3")
                os.remove("selectLang.mp3")

                mouseClickDetections.translateNextSec = True
                mouseClickDetections.currentlyTranslating = False

    def on_click(x, y, button, pressed):
        # detects the mouse coordinates via the mouse listener
        mousePressCoord = [0, 0]

        # checks if the mouse has been pressed
        if pressed:

            # checks if page screen shot has been previously made to avoid any bugs and errors with clicking

            if checkForHyperlinkPress():
                # tts of pressing hyperlink and how alt must be pressed to process new page
                tts = gtts.gTTS("You have activated a hyperlink, press Alt to use the screen "
                                "reader on the changed page", lang=userInterface.lang,
                                tld=userInterface.tld)
                tts.save("ttsPgChange.mp3")
                playsound("ttsPgChange.mp3")

                # remove extra files created for screen reading process

                os.remove('ttsPgChange.mp3')
                on_press.pgChange = True

    # NEW FEATURE - detects whether user has scrolled if so, won't allow screen reading until alt pressed again
    def on_scroll(x, y, dx, dy):
        mouseClickDetections.scrolledCount += 1
        if mouseClickDetections.altPressed and (mouseClickDetections.scrolledCount == 1):
            # tts of pressing hyperlink and how alt must be pressed to process new page
            tts = gtts.gTTS("You have scrolled, press Alt to use the screen "
                            "reader on the changed page", lang=userInterface.lang,
                            tld=userInterface.tld)
            tts.save("ttsPgChange.mp3")
            playsound("ttsPgChange.mp3")

            # remove extra files created for screen reading process

            os.remove('ttsPgChange.mp3')
            on_press.pgChange = True

    # used to listen for the key and mouse presses - (wowowo878787, StackOverFlow, 2019)
    # https://stackoverflow.com/questions/45973453/using-mouse-and-keyboard-listeners-together-in-python

    with keyboard.Listener(on_press=on_press) as kListener, mouse.Listener(on_click=on_click, on_scroll=on_scroll) \
            as mListener:
        kListener.join()
        mListener.join


def userInterface():
    # default accent for TTs

    userInterface.accent = "American"
    userInterface.accentIdx = 0
    userInterface.lang = "en"
    userInterface.tld = "com"

    # starter for running code

    userInterface.screenReaderLanguage = "Eng"
    tts = gtts.gTTS("Press the space bar to listen to the instructions", lang=userInterface.lang,
                    tld=userInterface.tld)
    tts.save("startSpeech.mp3")
    playsound("startSpeech.mp3")
    os.remove("startSpeech.mp3")

    # instructions in english for the program

    instructions = """This application is a screen reader that helps you navigate websites. 
    In order to use this screen reader go to the webpage that you want to be read 
    and press alt. When you press alt your mouse will be moved to the 
    bottom left of the page. To use the screen reader itself, hover over a section you want to be read
    and press x. In order to stop the program press Escape. 
    To change the dialect press D. In order to repeat the 
    instructions in English press the spacebar. To repeat the 
    instructions in arabic press A. To leave the instructions press L.
    You may now begin using the screen reader"""

    # instruction in arabic for the program

    instructionsAr = """ هذا التطبيق عبارة عن قارئ شاشة يساعدك على تصفح مواقع الويب.
    لاستخدام قارئ الشاشة هذا ، انتقل إلى صفحة الويب التي تريد قراءتها
    واضغط على بديل. عند الضغط على مفتاح بديل ، سيتم نقل الماوس إلى ملف
    أسفل يسار الصفحة. لاستخدام قارئ الشاشة نفسه ، مرر مؤشر الماوس فوق القسم الذي تريد قراءته
    واضغط على x. لإيقاف البرنامج اضغط Escape.
     لتكرار
    التعليمات باللغة الإنجليزية اضغط على مفتاح المسافة. لتكرار ال
    التعليمات في الصحافة العربية أ. لترك التعليمات اضغط L.
    يمكنك الآن البدء في استخدام قارئ الشاشة"""

    def on_press(key):

        # deals with errors with keyboard listener

        try:
            # if D is pressed, accent can be
            if key.char == "d":

                # instructions to select an accent for screen reader

                selectingAccentInstructions = """In order to select an accent press the up button. When you have found the 
                                                    accent you want to use for your screen reader, press enter and you can begin 
                                                    using the screen reader"""

                # reads instructions in arabic

                tts = gtts.gTTS(selectingAccentInstructions, lang=userInterface.lang,
                                tld=userInterface.tld)

                tts.save("selectingAccentInstructions.mp3")
                playsound("selectingAccentInstructions.mp3")
                os.remove("selectingAccentInstructions.mp3")

            # if a is pressed read instructions in arabic

            elif key.char == "a":

                # instructions in arabic

                tts = gtts.gTTS(instructionsAr, lang="ar")
                tts.save("instructionsArSpeech.mp3")
                playsound("instructionsArSpeech.mp3")
                os.remove("instructionsArSpeech.mp3")

                # if the last spoken instruction was in Arabic do OCR in Arabic

                userInterface.screenReaderLanguage = "Ar"

            # will leave the instructions page

            elif key.char == "l":

                # message for leaving instruction page
                if userInterface.screenReaderLanguage == "Eng":
                    tts = gtts.gTTS("Remember to press Alt when you are ready", lang=userInterface.lang,
                                    tld=userInterface.tld)
                    tts.save("leaveMessage.mp3")
                    playsound("leaveMessage.mp3")
                    os.remove("leaveMessage.mp3")
                elif userInterface.screenReaderLanguage == "Ar":
                    leaveMsgAr = "تذكر أن تضغط على Alt عندما تكون جاهزًا"
                    tts = gtts.gTTS(leaveMsgAr, lang="ar")
                    tts.save("leaveMessage.mp3")
                    playsound("leaveMessage.mp3")
                    os.remove("leaveMessage.mp3")

                return False

        except AttributeError:

            # reading instructions in English, default language

            if key == keyboard.Key.space:

                tts = gtts.gTTS(instructions, lang=userInterface.lang,
                                tld=userInterface.tld)
                tts.save("instructionsSpeech.mp3")
                playsound("instructionsSpeech.mp3")
                os.remove("instructionsSpeech.mp3")

                # if the last spoken instruction was in English do OCR in English

                userInterface.screenReaderLanguage = "Eng"

            # an accent has been selected

            elif key == keyboard.Key.enter:

                # closing statement before instructions is closed

                tts = gtts.gTTS("Remember to press Alt when you are ready", lang=userInterface.lang,
                                tld=userInterface.tld)
                tts.save("leaveMessage.mp3")
                playsound("leaveMessage.mp3")
                os.remove("leaveMessage.mp3")

                # when enter is clicked, accent is selected and keyboard listener stops

                return False

            # change option of accent

            elif key == keyboard.Key.up:

                # options for the accent

                accentOptions = ["American", "Australian", "British", "French", "Spanish"]
                userInterface.accent = accentOptions[userInterface.accentIdx % len(accentOptions)]

                # if you want an American accent

                if userInterface.accent == "American":
                    userInterface.lang = "en"
                    userInterface.tld = "com"
                    tts = gtts.gTTS("American", lang=userInterface.lang,
                                    tld=userInterface.tld)
                    tts.save("accentChange.mp3")
                    playsound("accentChange.mp3")
                    os.remove("accentChange.mp3")

                # if you want an Australian accent

                elif userInterface.accent == "Australian":
                    userInterface.lang = "en"
                    userInterface.tld = "com.au"
                    tts = gtts.gTTS("Australian", lang=userInterface.lang,
                                    tld=userInterface.tld)
                    tts.save("accentChange.mp3")
                    playsound("accentChange.mp3")
                    os.remove("accentChange.mp3")

                # if you want an British accent

                elif userInterface.accent == "British":
                    userInterface.lang = "en"
                    userInterface.tld = "co.uk"
                    tts = gtts.gTTS("British", lang=userInterface.lang,
                                    tld=userInterface.tld)
                    tts.save("accentChange.mp3")
                    playsound("accentChange.mp3")
                    os.remove("accentChange.mp3")

                # if you want an Spanish accent

                elif userInterface.accent == "Spanish":
                    userInterface.lang = "es"
                    userInterface.tld = "es"
                    tts = gtts.gTTS("Spanish", lang=userInterface.lang,
                                    tld=userInterface.tld)
                    tts.save("accentChange.mp3")
                    playsound("accentChange.mp3")
                    os.remove("accentChange.mp3")

                # if you want an French accent

                elif userInterface.accent == "French":
                    userInterface.lang = "fr"
                    userInterface.tld = "fr"
                    tts = gtts.gTTS("French", lang=userInterface.lang,
                                    tld=userInterface.tld)
                    tts.save("accentChange.mp3")
                    playsound("accentChange.mp3")
                    os.remove("accentChange.mp3")

                # selection changes everytime up is pressed

                userInterface.accentIdx += 1

    with keyboard.Listener(on_press=on_press) as kListener:
        kListener.join()

    # Depending on the last language instructions were spoken in the screen reader will perform OCR in that language

    if userInterface.screenReaderLanguage == "Eng":
        mouseClickDetections()
    elif userInterface.screenReaderLanguage == "Ar":
        # Arabic version has less features
        mouseClickDetectionsAr()


userInterface()
