import os
from PIL import Image
import pytesseract
import fitz
import random
import pickle
import cv2 as cv
import re
from pathlib import Path
from scipy.ndimage import interpolation as inter
import numpy as np
import sys
replace = False
print("Add tesseract configuration here")
#tessdata_dir_config = r' --psm 1 --oem 1'

kuerzel = int(sys.argv[1])
path = "pdfs/"
kuerzel = os.listdir(path)[kuerzel]
save_path = "ocr/"

def pix2np(pix):
    im = np.frombuffer(pix.samples, dtype=np.uint8).reshape(pix.h, pix.w, pix.n)
    im = np.ascontiguousarray(im[..., [2, 1, 0]])  # rgb to bgr
    return im


"""
Edited version of https://github.com/PyImageSearch/imutils/blob/master/imutils/convenience.py
to add default background color of white
"""

def rotate_bound(image, angle):
    # grab the dimensions of the image and then determine the
    # center
    (h, w) = image.shape[:2]
    (cX, cY) = (w / 2, h / 2)
    # grab the rotation matrix (applying the negative of the
    # angle to rotate clockwise), then grab the sine and cosine
    # (i.e., the rotation components of the matrix)
    M = cv.getRotationMatrix2D((cX, cY), -angle, 1.0)
    cos = np.abs(M[0, 0])
    sin = np.abs(M[0, 1])
    # compute the new bounding dimensions of the image
    nW = int((h * sin) + (w * cos))
    nH = int((h * cos) + (w * sin))
    # adjust the rotation matrix to take into account translation
    M[0, 2] += (nW / 2) - cX
    M[1, 2] += (nH / 2) - cY
    # perform the actual rotation and return the image
    return cv.warpAffine(image, M, (nW, nH), borderValue=255)


def skew_score(pic, angle):
    rotated = rotate_bound(pic, angle)
    row_sums = np.sum(255-rotated, axis=1)
    #score = np.sum((row_sums[1:] - row_sums[:-1]) ** 2, dtype=float)
    score = np.var(row_sums)
    return row_sums, score


def rotate_best(image, angle_range):
    #get best angle
    angles = np.arange(-angle_range, angle_range, 0.05)
    best_score = 0
    best_angle = 0
    for angle in angles:
        sm, score = skew_score(image, angle)
        if score > best_score:
            best_score = score
            best_angle = angle
    # rotate image
    rot_img = rotate_bound(image, best_angle)
    return rot_img, best_angle

path = "pdfs/" + kuerzel + "/"
Path(save_path + kuerzel + "/").mkdir(parents=True, exist_ok=True)
files = os.listdir(path)
random.shuffle(files)
for filePath in files:
    if not os.path.isfile(save_path + kuerzel + "/" + re.match(r"(.*)\.pdf", filePath.lower()).group(1) + ".pickle") or replace:
        pdfFileObj = fitz.open("/work/smkblang/drucksachen/" + path + filePath)
        current_doc = []
        for pageObj in pdfFileObj:
            current_doc.append(pageObj.get_text())
        if sum([len(x.split()) for x in current_doc]) > 500 and not "WP01" in kuerzel:
            print("no tesseract neccessary")
            pickle.dump(current_doc, open(save_path + kuerzel + "/" + re.match(r"(.*)\.pdf", filePath.lower()).group(1) + ".pickle", "wb"))
        else:
            session = []
            for pageObj in pdfFileObj:
                pix = pageObj.get_pixmap(dpi=300)
                gray = cv.cvtColor(pix2np(pix).astype(np.uint8), cv.COLOR_BGR2GRAY)
                _, temp_image = cv.threshold(gray.astype(np.uint8), 0, 255, cv.THRESH_BINARY+cv.THRESH_OTSU)
                _, angle = rotate_best(temp_image.astype(np.uint8), 3)
                final_image = rotate_bound(gray, angle)
                _, final_image = cv.threshold(final_image.astype(np.uint8), 0, 255, cv.THRESH_BINARY+cv.THRESH_OTSU)
                image_data = Image.fromarray(final_image)
                if "WP01" in kuerzel:
                    session.append(pytesseract.image_to_string(image_data, lang="tessFrak", config=tessdata_dir_config)                )
                else:
                    session.append(pytesseract.image_to_string(image_data, lang="deu", config='--psm 1 --oem 1'))
            pickle.dump(session, open(save_path + kuerzel + "/" + re.match(r"(.*)\.pdf", filePath.lower()).group(1) + ".pickle", "wb"))
