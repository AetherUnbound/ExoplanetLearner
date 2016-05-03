import mysql.connector
import math
import sys
import numpy as np
import matplotlib.pyplot as plt
from matplotlib import cm


#Variable declaration space
#External login reference
execfile("../Login/login.py")

#Parameter vector
#theta = [1, 2, -0.025]
theta = [600, 0, 0]
#theta = [0, 0, 0]
x = []
y = []
z = []

##Function declaration##

#Preparation function
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

#Hypothesis function
#   Takes a specific instance and calculates
#   the 'hypothesis value' for it
#   Range: -inf < x < inf
def h(x):
    global theta
    hyp = 0
    for index, item in enumerate(x):
        #sum of parameter vector times actual value
        if(index < len(x) - 1): #don't want to include classification
            dumb = theta[index]
            hyp += (dumb * item)
    hyp = logit(hyp)
    return (hyp)

#Logit Function
#   This function gives a probability value based off
#   of the calculated 'hypothesis value'.
#   Range: 0 < x < 1
def logit(val):
    if (val > 709): #more than exp can handle
        return 0.999999999999
    elif (val < -709): #opposite end
        return sys.float_info.min
    else:
        toreturn = 1/(1+math.exp(-val))
        return 0.999999999999 if toreturn == 1 else toreturn
    #### NEED THIS TO BE JUST LESS THAN ONE

#Cost Function
#   Determines a cost for the current values of theta
#   Range: 0 < x < inf
def J(rows):
    sum = 0
    length = len(rows)
    for i in range(0, length):
        x = h(rows[i])
        y = rows[i][len(rows[i])-1] #after inserting x0=1
        try:
            if (y == 1): #essentially y(i) * log(h(x(i)))
                sum += math.log(x)
            else: #(1-y(i)) * log(1-h(x(i)))
                sum += math.log(1-x)
        except ValueError: #incase it throws a -inf error
            print("ERROR ROWS: {} \t ERROR THETA: {}".format(rows[i],theta))
            h(rows[i])
            break
    #needs to be two separate operations in order to
    #return a valid number
    sum = sum * -1
    sum = sum/length
    return sum

#Derivative of Cost Function
#   Determines the derivative for the cost function
#   This is used in the gradient descent tuning
def delJ(rows, param):
    sum = 0
    length = len(rows)
    for i in range(0, length):
        x = rows[i]
        y = rows[i][len(x)-1] #after inserting x0=1
        sum += (h(x) - y) * x[param]
    sum = float(sum)/length
    return sum

#Theta Iteration
#   Update each theta value
def newTheta(rows, learnRate, numParams):
    global theta
    tmpTheta = [0, 0, 0]
    for i in range (0, numParams):
        tmpTheta[i] = theta[i] - (learnRate * delJ(rows, i))
    theta = tmpTheta

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

#Graphing function
#   Graphs the data points and calculated decision boundary
def graph(bounds):
    global x, y
    fig = plt.figure(figsize=(8,8))
    ax = fig.add_subplot(111)
    ax.set_title("Mag vs TEff",fontsize=14)
    ax.set_xlabel("Mag",fontsize=12)
    ax.set_ylabel("TEff",fontsize=12)
    ax.grid(True,linestyle='-',color='0.75')
    #x1 = np.random.random(30)
    #y1 = np.random.random(30)
    #z = np.random.random(30)
    xvar = np.asarray(x)
    yvar = np.asarray(y)
    zvar = np.asarray(z)
    #print(xvar)
    for i in range(0, len(bounds)):
        line = bounds[i]
        lx = [5, 20]
        ll = []
        for index, item in enumerate(lx):
            ll.append(line[0]*item + line[1])
        ax.plot(lx,ll, 'k-')
    # scatter with colormap mapping to z value
    #ax.scatter(x1,y1,s=20,c=z, marker = 'o', cmap = cm.jet );

    # scatter with colormap mapping to z value
    ax.scatter(xvar,yvar, 20, zvar, 'o', cmap = cm.jet)

    plt.show()

#SQL queries and modifications
cnx = mysql.connector.connect(**config)
cursor = cnx.cursor()


query = ("SELECT kpmag, teff, classif FROM trainingset2d") # WHERE testID IN ('1', '2', '3', '200', '201')")
#query = ("SELECT dist, kpmag, teff, classif FROM minitest WHERE testID IN ('1', '2', '3', '40', '41')")
cursor.execute(query)
rows = cursor.fetchall()
rows = prep(rows)
bounds = []
print(rows)
#print(rows[1][2])
print("Hypothesis value for row 1: {}".format(h(rows[1])))
#print("Total cost value: {}".format(J(rows)))
for i in range (0, 500):
    #print("Current Theta: {}".format(theta))
    cost = J(rows)
    #print("Current cost:  {} -- {} ".format(i, cost))
    #print("{},{}".format(i, cost))
    newTheta(rows, 0.01, 3) #for 600,0,0 theta
    #newTheta(rows, 0.0021, 3) #for 0-> theta
    #newTheta(rows, 0.001, 4)
    if(i > 0):
        bounds.append(decBound())
    if(cost == 0):
        break
print("Final theta {}".format(theta))
graph(bounds)
#for (no, dist, mag, teff, classif) in rows:
#    print("Distance: {}  \t Magnitude: {}  \t TEff: {} \t Class: {} ".format(dist, mag, teff, classif))


cursor.close()
cnx.close()