import numpy as np
import cv2
from math import floor
import pytesseract


def clamp(x, min, max):
    if x < min:
        return min
    elif x > max:
        return max

    return x


def tryGetPlateNum(img):
    # abcdefghijklmnopqrstuvwxyz
    config = r'--oem 1 --psm 10 outputbase digits -c tessedit_char_whitelist=0123456789'
    c = pytesseract.image_to_string(cntImgSegment, 'eng', config).strip()

    if len(c) == 1 and str.isdigit(c):
        return c 

    return ""


def filterDigits(extractedDigits):

    yPositions = [x[0][1] for x in extractedDigits]

    # Percentile outlier filtering
    q48, q52 = np.percentile(yPositions, 48), np.percentile(yPositions, 52)
    iqr = q52 - q48
    cut_off = iqr
    lower, upper = q48 - cut_off, q52 + cut_off
    extractedDigits = [x for x in extractedDigits if x[0][1] >= lower and x[0][1] <= upper]
    return extractedDigits

    # Z score outlier filtering
    # mean = np.mean(yPositions, keepdims=True)
    # std = np.std(yPositions, keepdims=True)
    # zscore = np.abs((yPositions - mean) / std)
    # print('Z-Score:', zscore) 

    # for i in range(len(yPositions)-1, -1, -1):
    #     if zscore[i] >= 1.8:
    #         extractedDigits.pop(i)


pytesseract.pytesseract.tesseract_cmd = r'D:\Program Files\tesseract-ocr\tesseract.exe'

imgName = 'plate5.png'
imgColor = cv2.imread(imgName)
height, width, channels = imgColor.shape 

# Image pre-processing 
img = cv2.imread(imgName, cv2.IMREAD_GRAYSCALE)
cv2.imshow('1-input-img', img)

img = cv2.GaussianBlur(img, (3,3), 0)
cv2.imshow('2-blurred-img', img)

img = cv2.Laplacian(img, cv2.CV_8U)
cv2.imshow('test-input-img', img)

# img = cv2.add(img, np.array([80.0]))
# cv2.imshow('3-brightened-img', img)

# img = cv2.morphologyEx(img, cv2.MORPH_OPEN, np.ones((5, 5), np.uint8), iterations=1)
# cv2.imshow('4-eroded-img', img)

threshImg = cv2.adaptiveThreshold(img, 255, cv2.ADAPTIVE_THRESH_GAUSSIAN_C, cv2.THRESH_BINARY, 11, 2)
cv2.imshow('5-thresh-img', threshImg)

# Find all contours
cnts, h = cv2.findContours(threshImg, cv2.RETR_LIST, cv2.CHAIN_APPROX_NONE)

# Remove 90% smallest contours
cntAreas = []
for cnt in cnts:
    cntAreas.append(cv2.contourArea(cnt))

cntsByArea = [x for _, x in sorted(zip(cntAreas, cnts), key=lambda pair: pair[0])]
cnts = cntsByArea[floor(len(cntsByArea)*0.9):]

# Draw all remaining cnts
imgWithContoursAll = cv2.drawContours(imgColor, cnts, -1, (0, 0, 255), 1)
cv2.imshow('5-contours-img', imgColor)
cv2.waitKey()
exit(0)

# Extract letters
extractedDigits = []
for i in range(len(cnts)-1, -1, -1):

    cnt = cnts[i]
    x, y, w, h = cv2.boundingRect(cnt)

    # Expand rect a bit so the detector works
    offset = 2
    x = clamp(x-offset, 0, width)
    y = clamp(y-offset, 0, height)
    w = clamp(w+offset*2, 0, width)
    h = clamp(h+offset*2, 0, height)

    # Highlight the contour we are trying to get characters from
    temp = imgColor
    cv2.rectangle(temp, (x, y), (x+w, y+h), (255, 0, 0), 2)
    cv2.imshow('5-contours-img', temp)

    cntImgSegment = threshImg[y:y + h, x:x + w]
    char = tryGetPlateNum(cntImgSegment)
    if char != "":
        extractedDigits.append((((x+w)/2, (y+h)/2), char))
        # print(char)

    # cv2.waitKey(0)

print('Extracted digits randomly ordered:', extractedDigits)

# Remove wrongly detected digits by removing outilers in the y-pos
# extractedDigits = filterDigits(extractedDigits)
# print('Filtered digits using y-position:', extractedDigits)

extractedDigits = [x for _, x in sorted(extractedDigits, key=lambda pair: pair[0][0])]
print('Extracted digits ordered by x-position:', extractedDigits)

cv2.waitKey(0)
