# histogram_utils.py
import cv2
from matplotlib import pyplot as plt

def show_histogram(img):
    color = ('b', 'g', 'r')
    plt.figure("Histogram")
    for i, col in enumerate(color):
        hist = cv2.calcHist([img], [i], None, [256], [0, 256])
        plt.plot(hist, color=col)
        plt.xlim([0, 256])
    plt.title("Histogram Warna")
    plt.xlabel("Intensitas")
    plt.ylabel("Jumlah Pixel")
    plt.show()
