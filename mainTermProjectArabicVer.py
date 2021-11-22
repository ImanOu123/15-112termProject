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


def distinguishSectionsAr(img):
    # perform OCR on screenshot of full page
    custom_config = r'--oem 3 --psm 1'
    string = pytesseract.image_to_string(img, config=custom_config, lang="ara")

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
                                         config=custom_config, lang="ara")
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
    def combineSectionsAr(minMaxDict, text1, text2):
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
                        newText, newCoord = combineSectionsAr(minMaxCoord, text, elem)
                        combinedTexts += [text, elem]
                        # create a new dictionary with the bigger sections
                        newMinMaxCoord[newText] = newCoord

    # for small sections that weren't combined and sections that weren't small, add to new dictionary
    for i in minMaxCoord:
        if i not in smallSections or (i in smallSections and i not in combinedTexts):
            newMinMaxCoord[i] = [minMaxCoord[i][0], minMaxCoord[i][1], minMaxCoord[i][2], minMaxCoord[i][3]]

    return newMinMaxCoord


def mouseClickDetectionsAr():
    # in order to run the program, the user must press alt
    def on_press(key):
        # when alt key pressed start listening for a mouse press
        if key == keyboard.Key.alt:
            # moves mouse to the top left of the page
            mouse = Controller()
            mouse.position = (0, 1080)
            mouseMoveStr = "تم نقل الماوس إلى أسفل يسار الصفحة"
            tts = gtts.gTTS(mouseMoveStr, lang="ar")
            tts.save("mouseMove.mp3")
            playsound("mouseMove.mp3")
            os.remove("mouseMove.mp3")

            # takes a screenshot of the current page - region doesn't include address bar -
            # may need to adjust to fit screen
            img = pyautogui.screenshot('fullPgScreenshot.png', region=(0, 100, 1440, 900))

            # convert image from png to jpg so it can be used for the OCR - Grayscale is for better recognition
            pngToJpg = cv2.imread('fullPgScreenshot.png', cv2.IMREAD_GRAYSCALE)
            cv2.imwrite('fullPgScreenshot.jpg', pngToJpg)

            # extract sections of webpage
            on_press.stringWCoordDict = distinguishSectionsAr('fullPgScreenshot.jpg')

            # When the page is prepared for TTS
            prepClicking = "يمكنك الآن البدء في النقر فوق"
            tts = gtts.gTTS(prepClicking, lang="ar")
            tts.save("prepClicking.mp3")
            playsound("prepClicking.mp3")
            os.remove("prepClicking.mp3")

            # page change variable, won't read any text until Alt is pressed again
            on_press.pgChange = False

        elif key == keyboard.Key.esc:
            goodByeStr = "مع السلامة. شكرا لك على استخدام قارئ الشاشة."
            tts = gtts.gTTS(goodByeStr, lang="ar")
            tts.save("goodBye.mp3")
            playsound("goodBye.mp3")
            os.remove("goodBye.mp3")
            # remove extra files
            os.remove("fullPgScreenshot.jpg")
            # Stop mouse and keyboard listeners
            mListener.stop()
            return False

    def on_click(x, y, button, pressed):
        mousePressCoord = [0, 0]
        try:
            stringWCoordDict = on_press.stringWCoordDict
        except:
            stringWCoordDict = {}

        if pressed:
            # receive mouse press coordinates
            mousePressCoord = [x, y - 100]

            # take a screenshot to compare with original screenshot to check if hyperlink was pressed
            im = pyautogui.screenshot('comparePgScreenshot.png', region=(0, 100, 1440, 900))

            # convert image from png to jpg so it can be used for the OCR - Grayscale is for better recognition
            pngToJpg = cv2.imread('comparePgScreenshot.png', cv2.IMREAD_GRAYSCALE)
            cv2.imwrite('comparePgScreenshot.jpg', pngToJpg)

            # check if two screenshots are the same - (abhi, StackOverFlow, 2020)
            # https://stackoverflow.com/questions/1927660/compare-two-images-the-python-linux-way
            with open('fullPgScreenshot.jpg', 'rb') as f:
                content1 = f.read()
            with open('comparePgScreenshot.jpg', 'rb') as f:
                content2 = f.read()
            if content1 != content2:
                # perform text to speech on string
                pgChangeStr = "لقد قمت بتنشيط ارتباط" \
                              " تشعبي أو قمت بالتمرير ، اضغط على Alt لاستخدام قارئ الشاشة على الصفحة التي تم تغييرها"
                tts = gtts.gTTS(pgChangeStr, lang="ar")
                tts.save("ttsPgChange.mp3")
                playsound("ttsPgChange.mp3")

                # remove extra files created for screen reading process
                os.remove('ttsPgChange.mp3')
                on_press.pgChange = True

            # remove unnecessary files
            os.remove('comparePgScreenshot.jpg')
            os.remove('comparePgScreenshot.png')

        # check if page hasn't been changed with last click
        if not on_press.pgChange:
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
            pgChange = False

    # used to listen for the key and mouse presses - (wowowo878787, StackOverFlow, 2019)
    # https://stackoverflow.com/questions/45973453/using-mouse-and-keyboard-listeners-together-in-python

    with keyboard.Listener(on_press=on_press) as kListener, mouse.Listener(on_click=on_click) as mListener:
        kListener.join()
        mListener.join()


mouseClickDetectionsAr()