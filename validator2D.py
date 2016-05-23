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
theta = [0,0,0]
#boundary = param[numParam:]
#print(boundary)
c = []
x = []
y = []
z = []
m1 = -84.8089995193
b1 = 5964.5755606
m2 = -45.5079023429
b2 = 6425.79324464

##Function declaration##

# Preparation function
#   Adds 1 to x_0 value for intercept calculations
def prep(rows):
    for i in range(0, len(rows)):
        rows[i] = list(rows[i])
        rows[i].insert(0, 1)
        x.append(rows[i][1])
        y.append(rows[i][2])
        z.append(rows[i][3])
        rows[i][2] /= 100
        #no idea if this will change anything
    return rows


# Hypothesis function
#   Since we have 2 lines for the 2D data set, this
#   hypothesis function will determine class solely
#   based of a points position within or without the
#   two boundary lines
def h(x):
    global m1, b1, m2, b2
    teff = x[2] * 100
    mag = x[1]
    if((teff > (m1 * mag) + b1)
    and (teff < (m2 * mag) + b2)):
        return 0.75
    else: #outside region
        return 0.25

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

#Decision Boundary
#   Determines the linear equation for the decision boundary
def decBound():
    global theta
    m = -((100 * theta[1])/theta[2])
    b = -((100 * theta[0])/theta[2])
    #m = -((theta[1])/theta[2])
    #b = -((theta[0])/theta[2])
    print("y = {}x + {}".format(m, b))
    line = [m, b]
    return line

# Graphing function
#   Graphs the data points and calculated decision boundary
def graph():
    global x, y, m1, b1, m2, b2
    fig = plt.figure(figsize=(8,8))
    ax = fig.add_subplot(111)
    #ax = fig.gca(projection = '3d')
    plt.hold(True)
    ax.set_title("Mag vs TEff",fontsize=14)
    ax.set_xlabel("Mag",fontsize=12)
    ax.set_ylabel("TEff",fontsize=12)
    ax.grid(True,linestyle='-',color='0.75')
    xvar = np.asarray(x)
    yvar = np.asarray(y)
    zvar = np.asarray(z)

    #determines line of best fit
    #m, b = np.polyfit(xvar, yvar, 1)
    #x_line = [min(xvar), max(xvar)]
    #y_line = [m*xx + b for xx in x_line]
    #ax.plot(x_line, y_line, '-')
    #print(str(m) + " " + str(b))

    line1x = [5, 20]
    line1y = []
    for index, item in enumerate(line1x):
        line1y.append(m1*item + b1)
    line2x = [5, 20]
    line2y = []
    for index, item in enumerate(line2x):
        line2y.append(m2 * item + b2)
    ax.plot(line1x,line1y, 'k-')
    ax.plot(line2x,line2y, 'k-')
    # scatter with colormap mapping to z value
    #ax.scatter(x1,y1,s=20,c=z, marker = 'o', cmap = cm.jet );

    # scatter with colormap mapping to z value
    ax.scatter(xvar,yvar, 20, zvar, 'o', cmap = cm.jet)

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
query = ("SELECT kpmag, teff, classif FROM trainingset2d") # WHERE testID IN ('1', '2', '3', '200', '201')")
#query = ("SELECT kpmag, teff, dist, classif FROM minitest WHERE testID IN ('1', '2', '3', '40', '41')")
cursor.execute(query)
rows = cursor.fetchall()
rows = prep(rows)
print(rows)
# print(rows[1][2])
print("Hypothesis value for row 1: {}".format(h(rows[1])))
count = 0
numData = len(rows)
for i in range(0, len(rows)):
    currRow = rows[i]
    currHyp = h(currRow)
    truth = isRightClass(currHyp, currRow[-1])
    if(not truth):
        count += 1
    print("RowID: {}  RowVal: {}  HVal: {}  RightClass: {}".format(i, currRow, currHyp, truth))

percentage = (float(numData - count) / numData) * 100
print("Number incorrectly classified: {}/{}".format(count, numData))
print("Percentage correct: {}%".format(percentage))
tFile = open('BoundValues\\result ' + str(theta) + ".txt", "w")
tFile.write(str(theta) + '\n' + str(count) + "\n" + str(numData) + '\n' + str(percentage))
#jList = [count, numData, percentage]
#json.dump(jList, tFile)
graph()

cursor.close()
cnx.close()
