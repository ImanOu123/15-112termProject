# TEXT TO SPEECH

# import gtts
# from playsound import playsound
#
# tts = gtts.gTTS("Hello world")
# tts.save("hello.mp3")
# playsound("hello.mp3")
#
# # SCREEN SHARING
#
import pyautogui
# im2 = pyautogui.screenshot('my_screenshot2.png', region=(0,0,1920,1080))

# DETECTING MOUSE CLICKS

from pynput.mouse import Button, Controller
#
# mouse = Controller()

# Read pointer position
# print('The current pointer position is {0}'.format(
#     mouse.position))

# Set pointer position
# mouse.position = (10, 20)
# print('Now we have moved it to {0}'.format(
#     mouse.position))

# mouse.click(Button.left, 2)

from pynput.mouse import Listener

# def on_move(x, y):
#     print('Pointer moved to {0}'.format(
#         (x, y)))
#
#
# def on_click(x, y, button, pressed):
#     print('{0} at {1}'.format(
#         'Pressed' if pressed else 'Released',
#         (x, y)))
#     # if not pressed:
#     #     # Stop listener
#     #     return False
#
#
# def on_scroll(x, y, dx, dy):
#     print('Scrolled {0}'.format(
#         (x, y)))


# Collect events until released
# with Listener(
#         # on_move=on_move,
#         on_click=on_click) as listener:
#     # on_scroll=on_scroll)
#     listener.join()

# OPTICAL CHARACTER RECOGNITION
# import cv2
# import pytesseract
#
# img = cv2.imread('image.jpg')
#
# # Adding custom options
# custom_config = r'--oem 3 --psm 6'
# print(pytesseract.image_to_string(img, config=custom_config))

# from pynput.mouse import Listener
#
# def on_click(x, y, button, pressed):
#     print('{0} at {1}'.format(
#         'Pressed' if pressed else 'Released',
#         (x, y)))
#
#
# with Listener(on_click=on_click) as listener:
#     listener.join()

# yCoord = 0
# xCoord = 0
# counter = 0
# xLis = []
# yLis = []
# maxX = 0
# for text, top, left, width, height in zip(dict["text"], dict["top"],
#                                           dict["left"], dict["width"],
#                                           dict["height"]):
#     if text in ["The", "cat", "(Felis", "catus)"]:
#         if counter == 1:
#             yCoord = top
#             xCoord = left
#         counter += 1
#
#     if counter >= 1 and yCoord - 10 < top < yCoord + 10:
#         # img = cv2.rectangle(img, (left, top), (left + width, top + height),
#         #                     (0, 255, 0), 2)
#         xLis.append(left)
#         yLis.append(top)
#         if left == max(xLis):
#             maxX = left + width
#     elif counter >= 1 and xCoord - 10 < left < maxX:
#         # img = cv2.rectangle(img, (left, top), (left + width, top + height),
#         #                     (0, 255, 0), 2)
#         xLis.append(left)
#         yLis.append(top)
# img = cv2.rectangle(img, (min(xLis), min(yLis)), (max(xLis), max(yLis)),
#                     (255, 0, 0), 2)
# # print(pytesseract.image_to_string(img, config=custom_config))
# cv2.imshow('img', img)
# cv2.waitKey(0)

import cv2
import pytesseract
from pytesseract import Output

img = cv2.imread('sampleImages/fullPage3.jpg')
# perform OCR on screenshot of full page
custom_config = r'--oem 3 --psm 1'
string = pytesseract.image_to_string(img, config=custom_config)

sectionsLst = string.split("\n\n")
cleanSectionLst = []

# create a new list of words seperated by section
for i in sectionsLst:
    cleanSectionLst.append(i.replace("\n", " ").split(" "))

# extra relevant data about the words on the image - coordinates
dataDict = pytesseract.image_to_data(img, output_type=Output.DICT,
                                     config=custom_config)
lstWords = list(dataDict["text"])

print(dataDict["text"])


def betterIdx(lst, word, num):
    # extracts the nth duplicate's index
    counter = 0
    for i in range(len(lst)):
        if lst[i] == "Zendure":
            print(counter, num)
        if lst[i] == word:
            counter += 1
        if counter == num:
            return i
    return len(lst)-1 # FIX THIS AND CHANGE ON MAIN FILE

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
                               dataDict["width"][val], dataDict["height"][val]])

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
for i in minMaxCoord:
    img = cv2.rectangle(img, (minMaxCoord[i][0], minMaxCoord[i][1]),
                        (minMaxCoord[i][2], minMaxCoord[i][3]), (255, 0, 0), 2)



cv2.imshow('img', img)
cv2.waitKey(0)
