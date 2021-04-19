import numpy as np
import cv2
from math import floor
import pytesseract
import matplotlib.pyplot as plt

pytesseract.pytesseract.tesseract_cmd = r'D:\Program Files\tesseract-ocr\tesseract.exe'
#pytesseract.pytesseract.tesseract_cmd = r'/usr/bin/tesseract'

class CharContour():
    def __init__(self, x, y, w, h, cnt):
        self.x = x
        self.y = y
        self.w = w
        self.h = h
        self.cnt = cnt
        self.char = '?'

    # We use this to ensure that two contours with the same bounding box are considered the same
    def __hash__(self):
        return hash((self.x, self.y, self.w, self.h))

    def __eq__(self, other):
        return self.x == other.x and self.y == other.y and self.w == other.w and self.h == other.h

    def __repr__(self):
        return self.char


def Clamp(x, min, max):
    if x < min:
        return min
    elif x > max:
        return max

    return x


def TryGetPlateNum(img):
    # ABCDEFGHIJKLMNOPQRSTUVWXYZ
    config = r'--oem 3 --psm 13 -c tessedit_char_whitelist=ABCDEFGHIJKLMNOPQRSTUVWXYZ0123456789'
    # config = r'--oem 1 --psm 10 outputbase digits -c tessedit_char_whitelist=0123456789'

    c = pytesseract.image_to_string(img, 'eng', config).strip()
    if len(c) == 0:
        return ''

    return c[0]


def isDigitAOne(char):
    ratio = char.w / char.h
    return ratio > 0.2 and ratio < 0.5


def FilterBoundingBoxes(chars):

    chars = list(set(chars))
    cntsToRemove = []

    # Remove non-external bounding boxes like the hole inside 4, inside 0 and so on
    for i in range(len(chars)):

        if chars[i] in cntsToRemove:
            continue

        x1, y1, w1, h1 = chars[i].x, chars[i].y, chars[i].w, chars[i].h
        cnt1Area = chars[i].w * chars[i].h

        for j in range(len(chars)):

            if i == j:
                continue

            x2, y2, w2, h2 = chars[j].x, chars[j].y, chars[j].w, chars[j].h

            # In case of too much overlap remove the smaller contour
            percentOverlap = GetPercentOverlap(x1, y1, w1, h1, x2, y2, w2, h2)
            if percentOverlap > 0.4:
                if cnt1Area < chars[j].w * chars[j].h:
                    cntsToRemove.append(chars[i])
                else:
                    cntsToRemove.append(chars[j])

    cntsToRemove = list(set(cntsToRemove))
    for c in cntsToRemove:
        chars.remove(c)

    return chars


def ContourWithinPlates(plates, x, y, w, h):

    for plate in plates:
        if GetPercentOverlap(x, y, w, h, plate[0], plate[1], plate[2], plate[3]) >= 0.4:
            return True

    return False

# Calculate the percent overlap between the two bounding boxes
def GetPercentOverlap(x1, y1, w1, h1, x2, y2, w2, h2):
    overlapX = max(0, min(x1 + w1, x2 + w2) - max(x1, x2))
    overlapY = max(0, min(y1 + h1, y2 + h2) - max(y1, y2))
    overlapArea = overlapX * overlapY

    return overlapArea / (w1 * h1)


def OCR(imgColor, morphedImg, chars):

    for c in chars:
        # Highlight the contour we are trying to get characters from
        temp = imgColor
        cv2.rectangle(temp, (c.x, c.y), (c.x + c.w, c.y + c.h), (255, 0, 0), 2)
        # cv2.imshow('6-contours-img', temp)

        cntImgSegment = morphedImg[c.y:c.y + c.h, c.x:c.x + c.w].copy()
        _, cntImgSegment = cv2.threshold(
            cntImgSegment, 0, 255, cv2.THRESH_OTSU | cv2.THRESH_BINARY_INV)

        ocrChar = TryGetPlateNum(cntImgSegment)
        if ocrChar == '' and isDigitAOne(c):
            ocrChar = '1'

        if ocrChar != '':
            c.char = ocrChar
            print('ocr', ocrChar)

        # cv2.waitKey(0)


def FilterOCR(chars):

    digitCount = 0
    avgCharArea = 0
    for c in chars:
        if c.char.isdigit():
            digitCount += 1
            avgCharArea += c.w * c.h

    if digitCount == 0:
        return chars

    charsToRemove = []
    avgCharArea /= float(digitCount)
    print('avgCharArea', avgCharArea)
    for c in chars:
        if c.char.isdigit() and abs(c.w * c.h - avgCharArea) / avgCharArea > 0.48:
            charsToRemove.append(c)

    for c in charsToRemove:
        chars.remove(c)

    return chars


def GetCarInfo(charsCnts):

    for i in range(len(charsCnts) - 1, -1, -1):
        if charsCnts[i].char == '?':
            charsCnts.pop(i)

    if len(charsCnts) == 0:
        return '', '', ''
            
    carNum = ''
    letter = ''
    city = ''

    if charsCnts[0].char.isalpha():
        letter = charsCnts[0].char
    elif charsCnts[-1].char.isalpha():
        letter = charsCnts[-1].char

    for i in range(len(charsCnts) - 1, -1, -1):

        c = charsCnts[i].char
        if c.isdigit() and len(carNum) < 5:
            carNum = c + carNum

    return letter, carNum, city


def GetPlateNumber(imgName):

    imgColor = cv2.imread(imgName)
    height, width, _ = imgColor.shape

    # Image pre-processing
    img = cv2.imread(imgName, cv2.IMREAD_GRAYSCALE)
    # cv2.imshow('1-original', img)

    img = cv2.add(img, np.array([50.0]))
    # cv2.imshow('2-brightened', img)
    img = cv2.GaussianBlur(img, (3, 3), 0)
    # cv2.imshow('2-brightened+blur', img)

    blackHatMorphKernel = cv2.getStructuringElement(cv2.MORPH_RECT, (19, 7))
    img = cv2.morphologyEx(img, cv2.MORPH_BLACKHAT, blackHatMorphKernel)
    morphedImg = img.copy()
    # cv2.imshow('3-morph-blackhat', img)

    # Detect plate area and ignore regions not within specific area within image
    plate = cv2.morphologyEx(morphedImg, cv2.MORPH_CLOSE,
                            cv2.getStructuringElement(cv2.MORPH_RECT, (19, 7)))
    # cv2.imshow('4.1-morph-closed', plate)

    plate = cv2.threshold(plate, 0, 255, cv2.THRESH_BINARY | cv2.THRESH_OTSU)[1]
    # cv2.imshow('4.2-threshold-OTSU', plate)

    plate = cv2.erode(plate, None, iterations=5)
    # cv2.imshow('4.3-erode', plate)

    plate = cv2.dilate(plate, None, iterations=15)
    # cv2.imshow('4.4-threshold-dilate', plate)

    cnts2 = cv2.findContours(plate, cv2.RETR_EXTERNAL, cv2.CHAIN_APPROX_SIMPLE)[0]
    cntAreas = []
    for cnt in cnts2:
        cntAreas.append(cv2.contourArea(cnt))

    cntsByArea = [x for _, x in sorted(zip(cntAreas, cnts2), key=lambda pair: pair[0], reverse=True)]
    cnts2 = cntsByArea[:10]

    cps = []
    candidatePlates = []
    for i in range(len(cnts2)-1, -1, -1):

        cnt = cnts2[i]
        x, y, w, h = cv2.boundingRect(cnt)

        minX = width * 0.3
        maxX = width * 0.7

        minY = height * 0.5
        maxY = height * 0.9

        posX = x + w * 0.5
        posY = y + h * 0.5
        if posX < minX or posX > maxX or posY < minY or posY > maxY:
            continue

        cps.append(cnt)
        candidatePlates.append((x, y, w, h))

    # cv2.imshow('4.5-chosen-plates', cv2.drawContours(imgColor.copy(), cps, -1, (255, 0, 0), 2))

    img = cv2.Canny(img, 50, 200)
    # cv2.imshow('5-canny-img', img)

    # Find all contours
    cnts = cv2.findContours(img, cv2.RETR_LIST, cv2.CHAIN_APPROX_SIMPLE)[0]

    # Remove 40% smallest contours
    cntAreas = []
    for cnt in cnts:
        cntAreas.append(cv2.contourArea(cnt))

    cntsByArea = [x for _, x in sorted(zip(cntAreas, cnts), key=lambda pair: pair[0])]
    cnts = cntsByArea[floor(len(cntsByArea) * 0.4):]

    # Draw all remaining cnts
    # cv2.imshow('all', cv2.drawContours(imgColor, cnts, -1, (0, 255, 0), 1))
    # cv2.waitKey()

    # Filter by AR and create contour objects
    charContours = []
    for i in range(len(cnts)-1, -1, -1):

        cnt = cnts[i]
        x, y, w, h = cv2.boundingRect(cnt)
        aspectRatio = w / float(h)
        if not(aspectRatio > 0.15 and aspectRatio < 0.9) or not(ContourWithinPlates(candidatePlates, x, y, w, h)):
            continue

        # Expand rect a bit so the detector works
        offset = 2
        x = Clamp(x-offset, 0, width)
        y = Clamp(y-offset, 0, height)
        w = Clamp(w+offset*2, 0, width)
        h = Clamp(h+offset*2, 0, height)

        charContours.append(CharContour(x, y, w, h, cnt))

    # Remove non-external bounding boxes
    charContours = FilterBoundingBoxes(charContours)
    OCR(imgColor, morphedImg, charContours)
    charContours = FilterOCR(charContours)

    charContours = sorted(charContours, key=lambda c: c.x)
    print('Extracted digits ordered by x-position:', charContours)

    carLetter, carNum, carCity = GetCarInfo(charContours)
    # cv2.waitKey(0)

    return carLetter, carNum, carCity

if __name__ == '__main__':
    letter, number, _ = GetPlateNumber('plate1.png')
    print('\nDetected car letter:', letter)
    print('Detected car number:', number)
