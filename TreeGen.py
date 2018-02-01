import numpy as np
import copy
from Tkinter import *
from CellularAutomata import *
import random, math


def distVecs(vec1, vec2):
    return np.linalg.norm(vec1 - vec2)


def magVec(vec):
    return sqrt(vec[0] ** 2 + vec[1] ** 2)


def normalizeVec(vec):
    return vec / np.linalg.norm(vec)


def stepTowards(current, goal, stepsize=1, noise=0.5):
    # stepvec = np.asarray([stepsize*(1+(rand/2-random.random()*rand)), stepsize*(1+(rand/2-random.random()*rand))])
    # step = np.multiply(normalizeVec(goal-current), stepvec)
    # step = normalizeVec(goal - current + np.random.rand(2) * rand) * stepsize
    if random.random() < noise:
        step = normalizeVec(np.random.rand(2)) * stepsize
    else:
        step = normalizeVec(goal - current) * stepsize
    current += step
    return current


def worldCreate(world):
    for i in range(len(world)):
        for j in range(len(world[0])):
            if world[i][j] == 1:
                w.create_rectangle(i * dispScale, j * dispScale, (i + 1) * dispScale, (j + 1) * dispScale,
                                   fill='#115533', width=0)
            if world[i][j] == 2:
                w.create_rectangle(i * dispScale, j * dispScale, (i + 1) * dispScale, (j + 1) * dispScale,
                                   fill='#220033', width=0)


def worldAddBranch(samples, r=15):
    for sample in samples:
        w.create_oval(sample[0] * dispScale, sample[1] * dispScale, (sample[0] + r) * dispScale,
                      (sample[1] + r) * dispScale, fill='#55FF99', width=0)


def createBranch(startpos, goalpos, stepsize=2, noise=0.5, threshold=0):
    samples = []
    current = startpos
    samples.append(copy.deepcopy(current))
    while distVecs(current, goalpos) > stepsize*5:
        if len(samples) > threshold:
            noise *= 0.99
        current = stepTowards(startpos, goalpos, stepsize, noise)
        samples.append(copy.deepcopy(current))
    return samples


def sampleValid(samples, sample):
    for s in samples:
        if distVecs(s, sample) < 20:
            return False
    return True


def addSubBranch(samples, mag=75):
    sample = random.choice(samples)

    subgoal = sample + np.asarray([random.randrange(-mag, mag), random.randrange(-mag, mag)])
    while not sampleValid(samples, subgoal):
        subgoal = sample + np.asarray([random.randrange(-mag, mag), random.randrange(-mag, mag)])

    subsamples = createBranch(sample, subgoal, stepsize=1, noise=0.4, threshold=10)
    return subsamples


def samples2world(world, samples, r=3):
    for s in samples:
        for i in range(-r, r + 1):
            for j in range(-r, r + 1):
                if 0 < int(s[0]) + i < len(world) - 1 and 0 < int(s[1]) + j < len(world[0]) - 1:
                    world[int(s[0]) + i][int(s[1]) + j] = 0.0

def placeTreasure(world, treasures):
    for s in treasures:
        for i in [-1, 0, 1]:
            for j in [-1, 0, 1]:
                if 0 < int(s[0]) + i < len(world) - 1 and 0 < int(s[1]) + j < len(world[0]) - 1:
                    world[int(s[0])+i][int(s[1])+j] = 2.0

def randomStartGoal(world, r=100):
    center = np.asarray([len(world) / 2.0, len(world[0]) / 2.0])
    theta1 = random.randrange(0, 360)
    theta2 = theta1 + random.randrange(90, 270)
    theta2 = theta2 % 360
    theta1 *= 3.14 / 180.0
    theta2 *= 3.14 / 180.0
    start = center + np.asarray([r * math.sin(theta1), r * math.cos(theta1)])
    goal = center + np.asarray([r * math.sin(theta2), r * math.cos(theta2)])
    return start, goal

def rectFree(world, x, y, w, h):
    for i in range(x, x+w):
        for j in range(y, y+h):
            if world[i][j] == 1:
                return False
    return True

def placeSquares(world, samples=10, size=20):
    tempWorld = copy.deepcopy(world)
    for s in range(samples):
        x = random.randrange(0, len(world))
        y = random.randrange(0, len(world[0]))
        if rectFree(tempWorld, x, y, size, size):
            for i in range(x, x + size):
                for j in range(y, y + size):
                    tempWorld[i][j] = 1
                    world[i][j] = 3


# random.seed(2)
# np.random.seed(2)
dispScale = 1
width = 400
height = 400
master = Tk()
w = Canvas(master, width=width * dispScale, height=height * dispScale, background='#42f46e')
w.pack()

world = [[1.0 for i in range(height)] for j in range(width)]
start, goal = randomStartGoal(world, r=100)

samples = createBranch(start, goal, stepsize=4, noise=0.5, threshold=25)
samples2world(world, samples, r=15)

subsamples = []
for i in range(10):
    subsamples += addSubBranch(samples, mag=random.randint(50,150))
samples2world(world, subsamples, r=random.randint(3,10))

treasures = []
subsubsamples = []
for i in range(15):
    subsubsamples += addSubBranch(subsamples)
    treasures.append(subsubsamples[-1])
samples2world(world, subsubsamples, r=1)



for i in range(3):
    filterSmooth(world, 4)
for i in range(15):
    filterEnlarge(world)
for i in range(3):
    filterSmooth(world, 4)

placeTreasure(world, treasures)
# placeSquares(world, samples=500, size=75)
# placeSquares(world, samples=100, size=30)

dispWorld(world, w, 1)
mainloop()
