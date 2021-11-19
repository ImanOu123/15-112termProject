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

    # create a new list of words seperated by section
    for i in sectionsLst:
        cleanSectionLst.append(i.replace("\n", " ").split(" "))

    # remove any unnecessary characters
    for i in range(len(cleanSectionLst)):
        if " " in cleanSectionLst[i]:
            cleanSectionLst[i].remove(" ")
        if "" in cleanSectionLst[i]:
            cleanSectionLst[i].remove("")

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

    return minMaxCoord

