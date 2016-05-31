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
        # adds each data value to an array for graphing later
        z.append(rows[i][1])
        y.append(rows[i][2] * 100)
        x.append(rows[i][3] * 10)
        c.append(rows[i][5])
        #rows[i][2] /= 100
        #rows[i][3] /= 10
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
            tmpT = theta[index]
            hyp += (tmpT * item)
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

#Assigning function
#   This function will assign a classification value based on the
#   calculated hypothesis value for the data point
def assign(hyp):
    if(hyp >= 0.5):
        return 1
    else: #hyp < 0.5
        return 0

# SQL queries and modifications
cnx = mysql.connector.connect(**config)
cursor = cnx.cursor()
updateCursor = cnx.cursor()
rows = []
count = 0
i = 0
for j in range(0, 150):
    #if(i > 500):
    #    break #testing purposes only
    query = ("SELECT id, kpmag, teff, dist FROM hip_assigned WHERE id='%i'" % int(j))
    cursor.execute(query)
    if(cursor.rowcount != 0): #if there actually exists such a row
        #i +=1
        row = cursor.fetchall()
        for (id, kepmag, teff, dist) in row:
            currRow = [1, kepmag, (teff/100), (dist/10), id]
            #dividing no longer occurs in preparing rows
            currHyp = h(currRow)
            classif = assign(currHyp)
            currRow.append(classif)
            rows.append(currRow)
            updateQuery = "UPDATE hip_assigned SET classif = %i WHERE id = '%i'" % (classif, currRow[4])
            print("RowID: {}  RowVal: {}  HVal: {}  Classification: {}".format(j, currRow, currHyp, classif))
            updateCursor.execute(updateQuery)
            cnx.commit()  # for committing changes made
prep(rows)
graph(decBound())

cursor.close()
cnx.close()
