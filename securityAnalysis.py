# -*- coding: utf-8 -*-

import matplotlib.pyplot as plt
import cv2
from PIL import Image
import math

i1 = cv2.imread('static/images/encryptedimages/p8.png',0)
h1 = cv2.calcHist([i1],[0],None,[256],[0,256])
plt.plot(h1)
plt.show()


testImg = 'static/images/encryptedimages/000.png'
img = Image.open(testImg)
img = img.convert("RGB")

img1 = Image.open('static/images/sample images/000.png')
img1 = img1.convert("RGB")

img2 = Image.open('static/images/decryptedimages/000.png')
img2 = img2.convert("RGB")

w, h = img.size
pixelList = []
for i in range(h):
    for j in range(w):
        R, G, B = img.getpixel((i, j))
        pixelList.append(R)
        
probabilityList = [0 for i in range(256)]
s = set(pixelList)
k = 0
for P in s:
    probabilityList[k] = pixelList.count(P)/65536
    k+=1
    
entropy = 0 #Expected value for good encryption is 8.
for i in range(256):
    entropy += (probabilityList[i] * math.log(1/probabilityList[i], 2))
    
print("Entropy:", entropy)
print()

s = 0
UACI = 0
d = 0
for i in range(h):
    for j in range(w):
        R1, G1, B1 = img1.getpixel((i, j))
        R2, G2, B2 = img2.getpixel((i, j))
        R3, G3, B3 = img.getpixel((i, j))
        s += pow(R1-R3, 2)
        if R1!=R3:
            d += 1
        UACI += (abs(R1-R3)/255)

MSE = s/65536
print("MSE: (between original and encrypted image)", MSE)
#MSE is the mean square error between ORIGINAL and ENCRYPTED IMAGE!

PSNR = 10*math.log10((255*255)/MSE)
print("PSNR:", PSNR)
#PSNR: Peak Signal to Noise Ratio - measures the distortion in the encrypted image compared to original image
print()

NPCR = d*100/(256*256)
print("NPCR:", NPCR)
#NPCR: number of pixels change rate: measures the % of pixels in encrypted image tht r diff from orig img

UACI = UACI/65536
print("UACI as %:", UACI*100)
#UACI: unified average changing intensity: avg change in the instensity from orig to encrypted img