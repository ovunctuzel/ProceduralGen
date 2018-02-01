from Tkinter import *
from PIL import Image
import random, copy
import cv2


def randomCell(prob):
    if random.random() <= prob:
        return 1
    else:
        return 0


def dispWorld(world, canvas, dispScale=1):
    for i in range(len(world)):
        for j in range(len(world[0])):
            if world[i][j] == 1:
                canvas.create_rectangle(i * dispScale, j * dispScale, (i + 1) * dispScale, (j + 1) * dispScale,
                                        fill='#115533', width=0)
            elif world[i][j] == 2:
                canvas.create_rectangle(i * dispScale, j * dispScale, (i + 1) * dispScale, (j + 1) * dispScale,
                                        fill='#221166', width=0)
            elif world[i][j] == 3:
                canvas.create_rectangle(i * dispScale, j * dispScale, (i + 1) * dispScale, (j + 1) * dispScale,
                                        fill='#A5FFAA', width=0)


def dispTreasurePotential(world):
    for i in range(len(world)):
        for j in range(len(world[0])):
            pot = getTreasurePotential((i, j), world) * 200 + 55
            if world[i][j] == 0:
                w.create_rectangle(i * dispScale, j * dispScale, (i + 1) * dispScale, (j + 1) * dispScale,
                                   fill='#%x%x%x' % (pot, pot, pot), width=0)


def getNeighborCt(cell, world):
    x = cell[0]
    y = cell[1]
    if x + 1 > len(world) - 1 or x - 1 < 0 or y + 1 > len(world[0]) - 1 or y - 1 < 0:
        return 8
    nbors = 0
    for i in range(-1, 2):
        for j in range(-1, 2):
            nbors += world[x + i][y + j]
    return nbors


def getTreasurePotential(cell, world, threshold=20):
    x = cell[0]
    y = cell[1]
    if world[x][y] == 1:
        return 0
    potential = 0
    for i in [-5, -4, -3, 3, 4, 5]:  # range(-3,4):
        for j in [-5, -4, -3, 3, 4, 5]:  # range(-3,4):
            if not (x + i > width - 1 or x + i < 0 or y + j > height - 1 or y + i < 0):
                if world[x + i][y + j] == 1:
                    potential += 1
    for i in [-2, -1, 1, 2]:  # range(-3,4):
        for j in [-2, -1, 1, 2]:  # range(-3,4):
            if not (x + i > width - 1 or x + i < 0 or y + j > height - 1 or y + i < 0):
                if world[x + i][y + j] == 1:
                    potential -= 3

    if potential < threshold:
        potential = 0
    return potential / 50.0


def filterSmooth(world, factor=4):
    for i in range(len(world)):
        for j in range(len(world[0])):
            if getNeighborCt((i, j), world) > factor:
                world[i][j] = 1
            else:
                world[i][j] = 0


def getRegionSize(cell, world):
    region = []
    frontier = [cell]
    val = world[cell[0]][cell[1]]
    c = 0
    while len(frontier) > 0 and c < width * height:
        item = frontier.pop()
        region.append(item)
        x = item[0]
        y = item[1]
        for i in [-1, 1]:
            for j in [-1, 1]:
                if (x + i, y + j) not in frontier and (x + i, y + j) not in region:
                    if not (x + i > width - 1 or x + i < 0 or y + j > height - 1 or y + i < 0) and world[x + i][
                                y + j] == val:
                        frontier.append((x + i, y + j))
        c += 1
    return len(region)


def purgeArea(x1, x2, y1, y2, world):
    for i in range(x1, x2):
        for j in range(y1, y2):
            world[i][j] = 0



def filterEnlarge(world, prob=0.8):
    newWorld = copy.deepcopy(world)
    width = len(world)
    height = len(world[0])
    for x in range(width):
        for y in range(height):
            if world[x][y] == 0:
                for i in range(-1, 2):
                    for j in range(-1, 2):
                        if not (x + i > width - 1 or x + i < 0 or y + j > height - 1 or y + i < 0):
                            if random.random() > prob:
                                newWorld[i + x][j + y] = 0
    for i in range(len(newWorld)):
        world[i] = newWorld[i]


def filterShrink(world, prob=0.8):
    newWorld = copy.deepcopy(world)
    for x in range(len(world)):
        for y in range(len(world[0])):
            if world[x][y] == 1:
                for i in range(-1, 2):
                    for j in range(-1, 2):
                        if not (x + i > width - 1 or x + i < 0 or y + j > height - 1 or y + i < 0):
                            if random.random() > prob:
                                newWorld[i + x][j + y] = 1
    for i in range(len(newWorld)):
        world[i] = newWorld[i]


def readWorld(imgpath):
    im = cv2.imread(imgpath, 0)
    return im


def combine(world, map):
    for x in range(len(world)):
        for y in range(len(world[0])):
            if map[x][y] == 0:
                world[x][y] = 2


def genWorld():
    startProb = 0.5
    world = [[randomCell(startProb) for i in range(height)] for j in range(width)]
    for i in range(5):
        filterSmooth(world, 4)
    for i in range(3):
        filterEnlarge(world)
    for i in range(5):
        filterSmooth(world, 4)
    for i in range(2):
        filterShrink(world)
    for i in range(5):
        filterSmooth(world, 4)
    purgeArea(100, 120, 0, 25, world)
    purgeArea(150, 160, 0, 60, world)
    purgeArea(0, 20, 100, 120, world)
    for i in range(5):
        filterSmooth(world, 4)
    return world


def reportRatio(world):
    total = 0.0
    for x in range(len(world)):
        total += sum(world[x])
    return total / (width * height)


if __name__ == "__main__":
    dispScale = 1
    width = 160
    height = 120
    master = Tk()
    w = Canvas(master, width=width * dispScale, height=height * dispScale, background='#42f46e')
    w.pack()

    while (True):
        world = genWorld()
        print
        reportRatio(world)
        if 0.4 < reportRatio(world) < 0.5:
            print
            "PASSED"
            break

    dispWorld(world)


    def callback(event):
        mx = int(w.canvasx(event.x))  # Translate mouse x screen coordinate to canvas coordinate
        my = int(w.canvasy(event.y))  # Translate mouse y screen coordinate to canvas coordinate
        # canvasobject = w.find_closest(mx, my, halo=5)  # get canvas object ID of where mouse pointer is
        print
        getRegionSize((mx, my), world)
        # print getTreasurePotential((mx, my), world)  # For you to visualize the canvas object number


    w.bind("<Button-1>", callback)

    mainloop()
