# morpho_operations.py
import cv2
import numpy as np

def apply_morphology(img):
    gray = cv2.cvtColor(img, cv2.COLOR_BGR2GRAY)
    _, binary = cv2.threshold(gray, 127, 255, cv2.THRESH_BINARY)
    
    se1 = cv2.getStructuringElement(cv2.MORPH_RECT, (5, 5))
    se2 = cv2.getStructuringElement(cv2.MORPH_ELLIPSE, (7, 7))
    dilated1 = cv2.dilate(binary, se1, iterations=1)
    dilated2 = cv2.dilate(binary, se2, iterations=1)

    combined = cv2.bitwise_or(dilated1, dilated2)
    return combined
