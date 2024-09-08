import sys
import numpy as np
from PIL import Image, ImageDraw
import math
import re

wallclr = 0, 0, 0, 255
pathclr = 255, 255, 255, 255
soluclr = 25, 121, 202, 255

def automaze(pic):
    # solution picture
    spic = pic
    if spic[0] == '.' and spic[1] == '\\':
        spic = "solution_" + spic[2:]
    # open and load image pixels
    img = Image.open(pic)
    px = img.load()
    # variable initialization
    sp, ep, x, y, mazeD, wallW = None, None, 0, 0, 16, 2
    pathW = mazeD - wallW
    mazeW = math.floor(img.size[0] / mazeD) * 2 + 1
    mazeH = math.floor(img.size[1] / mazeD) * 2 + 1
    mx, my = 0, 0
    # create a matrix for representing the path and wall
    matrix = np.zeros((mazeH, mazeW))
    # initialize the matrix - 0: wall, 1: path
    for y in range(mazeH):
        mx = 0
        for x in range(mazeW):
            if px[mx, my] == pathclr:
                matrix[y, x] = 1
            mx = mx + wallW if x % 2 == 0 else mx + pathW
        my = my + wallW if y % 2 == 0 else my + pathW
    # sum of horizontal and veritcal surrounding nodes
    smatrix = np.zeros((mazeH, mazeW))
    for r in range(mazeH):
        for c in range(mazeW):
            if matrix[r, c] == 1:
                # got a path
                if r == 0 or r == mazeH - 1:
                    # mark the Entrance and Exit node as 1
                    smatrix[r, c] = 1
                else:
                    # sum of horizontal and vertical surrounding nodes
                    smatrix[r, c] = np.sum(matrix[r-1:r+2, c]) + np.sum(matrix[r, c-1:c+2]) - 1
    # recusively remove dead end whose value is 2
    while True:
        deads = np.where(smatrix == 2)
        if len(deads[0]) == 0:
            # no more dead ends
            break
        pos = list(zip(deads[0], deads[1]))
        for p in pos:
            # decreasing value of dead end nodes and their horizontal and vertical adjacent nodes
            smatrix[p[0]-1:p[0]+2, p[1]] -= 1
            smatrix[p[0], p[1]-1:p[1]+2] -= 1
            smatrix[p] += 1
            # remove the dead end nodes
            matrix[p] = 0
    #smatrix[smatrix < 0] = 0

    # draw the solution on the maze
    mx, my = 0, 0
    for y in range(mazeH):
        mx = 0
        for x in range(mazeW):
            if matrix[y, x] == 1:
                if x % 2 == 0:
                    for i in range(2):
                        for j in range(14):
                            px[mx + i, my + j] = soluclr
                elif y % 2 == 0:
                    for i in range(14):
                        for j in range(2):
                            px[mx + i, my + j] = soluclr
                else:
                    for i in range(14):
                        for j in range(14):
                            px[mx + i, my + j] = soluclr
            mx = mx + wallW if x % 2 == 0 else mx + pathW
        my = my + wallW if y % 2 == 0 else my + pathW
    # save solution image
    img.save(spic)
    img.show()
    img.close()

def main():
    a='3.png'
    automaze(a)

if __name__ == "__main__":
    main()
