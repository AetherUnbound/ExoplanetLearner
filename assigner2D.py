import mysql.connector
import math
import sys
import numpy as np
import matplotlib.pyplot as plt
from mpl_toolkits.mplot3d import axes3d, Axes3D
from matplotlib import cm
from random import randint
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
        #rows[i] = list(rows[i])
        #rows[i].insert(0, 1)
        x.append(rows[i][1])
        y.append(rows[i][2])
        z.append(rows[i][4])
        #rows[i][2] /= 100
        #no idea if this will change anything
    return rows


# Hypothesis function
#   Since we have 2 lines for the 2D data set, this
#   hypothesis function will determine class solely
#   based of a points position within or without the
#   two boundary lines
def h(x):
    global m1, b1, m2, b2
    teff = x[2]
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

# Prep-z function
#   Prepares the row classification for proper output
def prepZ(rows):
    for i in range(0, len(rows)):
        z.append(rows[i][4])


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
#query = ("SELECT kepmag, teff, kepid FROM kepnoexo")
#cursor.execute(query)
#rows = cursor.fetchall()
#rows = prep(rows)
#print(rows)
# print(rows[1][2])
#print("Hypothesis value for row 1: {}".format(h(rows[1])))

#numData = len(rows)
i = 0
#currently at 198
for j in range(1, 573076):
    #if(i > 500):
    #    break #testing purposes only
    query = ("SELECT kepid, kepmag, teff FROM kepnoexo WHERE id='%i'" % int(j))
    cursor.execute(query)
    if(cursor.rowcount != 0): #if there actually exists such a row
        #i +=1
        row = cursor.fetchall()
        for (kepid, kepmag, teff) in row:
            currRow = [1, kepmag, teff, kepid]
            currHyp = h(currRow)
            classif = assign(currHyp)
            currRow.append(classif)
            rows.append(currRow)
            updateQuery = "UPDATE kepnoexo SET classif = %i WHERE kepid = '%i'" % (classif, currRow[3])
            print("KepID: {}  RowVal: {}  HVal: {}  Classification: {}".format(j, currRow, currHyp, classif))
            updateCursor.execute(updateQuery)
            cnx.commit()  # for committing changes made


#tFile = open('BoundValues\\result ' + str(theta) + ".txt", "w")
#tFile.write(str(theta) + '\n' + str(count) + "\n" + str(numData) + '\n' + str(percentage))
#jList = [count, numData, percentage]
#json.dump(jList, tFile)
prep(rows)
graph()

cursor.close()
cnx.close()
