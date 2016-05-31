import mysql.connector
import math
import sys
import numpy as np
import matplotlib.pyplot as plt
from mpl_toolkits.mplot3d import axes3d, Axes3D
from matplotlib import cm
from time import strftime
import json
import glob
import os

# Variable declaration space
# External login reference
execfile("../Login/login.py")

# Re-importing parameterization from most recent file
newest = max(glob.iglob('BoundValues\\trial*.txt'), key=os.path.getctime)
tFile = open(newest, "r")
print(newest)
param = json.load(tFile)
print(param)
numParam = param[0] + 1
theta = param[1:(numParam)]
print(theta)
tFile.close()
#boundary = param[numParam:]
#print(boundary)
c = []
x = []
y = []
z = []


##Function declaration##

# Preparation function
#   Adds 1 to x_0 value for intercept calculations
def prep(rows):
    for i in range(0, len(rows)):
        rows[i] = list(rows[i])
        rows[i].insert(0, 1)
        # adds each data value to an array for graphing later
        z.append(rows[i][1])
        y.append(rows[i][2])
        x.append(rows[i][3])
        c.append(rows[i][4])
        rows[i][2] /= 100
        rows[i][3] /= 10
    return rows


# Hypothesis function
#   Takes a specific instance and calculates
#   the 'hypothesis value' for it
#   Range: -inf < x < inf
def h(x):
    global theta
    hyp = 0
    for index, item in enumerate(x):
        # sum of parameter vector times actual value
        if (index < len(x) - 1):  # don't want to include classification
            dumb = theta[index]
            hyp += (dumb * item)
    hyp = logit(hyp)
    return (hyp)


# Logit Function
#   This function gives a probability value based off
#   of the calculated 'hypothesis value'.
#   Range: 0 < x < 1
def logit(val):
    if (val > 709):  # more than exp can handle
        return 0.999999999999
    elif (val < -709):  # opposite end
        return sys.float_info.min
    else:
        toreturn = 1 / (1 + math.exp(-val))
        return 0.999999999999 if toreturn == 1 else toreturn
        #### NEED THIS TO BE JUST LESS THAN ONE

# Decision Boundary
#   Determines the linear equation for the decision boundary
#   For a plane, this involves the following equation:
#   ax + by + cz + d = 0
#   But here, that equation will be:
#   z = d + ax + by (c will be inherent in those values)
def decBound():
    global theta
    d = -(theta[0] / theta[1])
    a = -(theta[3] / (10 * theta[1]))
    b = -theta[2] / (100 * theta[1])
    #print("z = {} + {}x + {}y".format(d, a, b))
    plane = [d, a, b]
    return plane

# Graphing function
#   Graphs the data points and calculated decision boundary
def graph(bounds):
    fig = plt.figure(figsize=(8, 8))
    ax = Axes3D(fig)
    # Plot options
    plt.hold(True)
    ax.set_title("Mag vs TEff vs Distance", fontsize=14)
    ax.set_zlabel("Mag", fontsize=12)
    ax.set_ylabel("TEff", fontsize=12)
    ax.set_xlabel("Distance", fontsize=12)
    ax.set_ylim(3000, 25000)
    ax.set_zlim(-5,20)
    ax.grid(True, linestyle='-', color='0.75')
    # Setting scatter plot variables up
    xvar = np.asarray(x)
    yvar = np.asarray(y)
    zvar = np.asarray(z)
    cvar = np.asarray(c)
    # Plane set up
    xx, yy = np.meshgrid(np.arange(0, 1000, 10), np.arange(3000, 10000, 100))
    plane = bounds
    # z = d + ax + by
    zz = plane[0] + plane[1] * xx + plane[2] * yy
    #zz[zz > 25] = np.nan

    ax.plot_surface(xx, yy, zz, color='black', alpha=0.25)

    # scatter 3D with colormap
    ax.scatter(xvar, yvar, zvar, c=cvar, marker='o', cmap=cm.jet)  # 20, zvar, 'o', cmap = cm.jet)

    plt.show()

# Classification assessment function
#   This will give true if the diving boundary correctly
#   classified a data point and false if it did not.
def isRightClass(hyp, act):
    if((act == 1 and hyp < 0.5) or (act ==0 and hyp > 0.5)):
        #False negative or false positive
        return False
    return True

# SQL queries and modifications
cnx = mysql.connector.connect(**config)
cursor = cnx.cursor()
query = ("SELECT kpmag, teff, dist, classif FROM validate3d")
cursor.execute(query)
rows = cursor.fetchall()
rows = prep(rows)
print(rows)
# print(rows[1][2])
print("Hypothesis value for row 1: {}".format(h(rows[1])))
count = 0
exoWrong = 0
totExo = 100 #from data set
numData = len(rows)
for i in range(0, len(rows)):
    currRow = rows[i]
    currHyp = h(currRow)
    truth = isRightClass(currHyp, currRow[-1])
    if(not truth):
        count += 1
        if(currRow[-1] == 1): #is an exoplanet
            exoWrong += 1
    print("RowID: {}  RowVal: {}  HVal: {}  RightClass: {}".format(i, currRow, currHyp, truth))

percentage = (float(numData - count) / numData) * 100
exoPerc = (float(totExo - exoWrong) / totExo) * 100
print("==TOTAL DATA==")
print("Number incorrectly classified: {}/{}".format(count, numData))
print("Percentage correct: {}%".format(percentage))
print("==EXOPLANET ONLY==")
print("Number incorrectly classified: {}/{}".format(exoWrong, totExo))
print("Percentage correct: {}%".format(exoPerc))
tFile = open('BoundValues\\result ' + str(theta) + ".txt", "w")
tFile.write(str(theta) + '\n' + str(count) + "\n" + str(numData) + '\n' + str(percentage))
#jList = [count, numData, percentage]
#json.dump(jList, tFile)
graph(decBound())

cursor.close()
cnx.close()
