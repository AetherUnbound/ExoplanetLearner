import mysql.connector
import math
import sys
import numpy as np
import matplotlib.pyplot as plt
from mpl_toolkits.mplot3d import axes3d, Axes3D
from matplotlib import cm

# Variable declaration space
# External login reference
execfile("../Login/login.py")

# Parameter vector
# theta = [1, 2, -0.025]
theta = [6, 1, 1, 1]
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
        # divide temperature values by a suitable number
        # in order for the algorithm to converge
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


# Cost Function
#   Determines a cost for the current values of theta
#   Range: 0 < x < inf
def J(rows):
    sum = 0
    length = len(rows)
    for i in range(0, length):
        x = h(rows[i])
        y = rows[i][len(rows[i]) - 1]  # after inserting x0=1
        try:
            if (y == 1):  # essentially y(i) * log(h(x(i)))
                sum += math.log(x)
            else:  # (1-y(i)) * log(1-h(x(i)))
                sum += math.log(1 - x)
        except ValueError:  # incase it throws a -inf error
            print("ERROR ROWS: {} \t ERROR THETA: {}".format(rows[i], theta))
            h(rows[i])
            break
    # needs to be two separate operations in order to
    # return a valid number
    sum = sum * -1
    sum = sum / length
    return sum


# Derivative of Cost Function
#   Determines the derivative for the cost function
#   This is used in the gradient descent tuning
def delJ(rows, param):
    sum = 0
    length = len(rows)
    for i in range(0, length):
        x = rows[i]
        y = rows[i][len(x) - 1]  # after inserting x0=1
        sum += (h(x) - y) * x[param]
    sum = float(sum) / length
    return sum


# Theta Iteration
#   Update each theta value
def newTheta(rows, learnRate, numParams):
    global theta
    tmpTheta = [0, 0, 0, 0]
    for i in range(0, numParams):
        tmpTheta[i] = theta[i] - (learnRate * delJ(rows, i))
    theta = tmpTheta


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
    print("z = {} + {}x + {}y".format(d, a, b))
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
    for i in range(0, len(bounds)):
        plane = bounds[i]
        # z = d + ax + by
        zz = plane[0] + plane[1] * xx + plane[2] * yy
        zz[zz > 25] = np.nan
        #zz[zz < -1000] = np.nan
        #for i in range(len(xx)):
        #    for j in range(len(yy)):
        #        if (zz[j, i] < -1000) or (zz[j, i] > 1000):
        #            zz[j, i] = float('nan')

        ax.plot_surface(xx, yy, zz, color='black', alpha=0.05)

    # scatter 3D with colormap
    ax.scatter(xvar, yvar, zvar, c=cvar, marker='o', cmap=cm.jet)  # 20, zvar, 'o', cmap = cm.jet)

    plt.show()


# SQL queries and modifications
cnx = mysql.connector.connect(**config)
cursor = cnx.cursor()

query = ("SELECT kpmag, teff, dist, classif FROM testingdata") # WHERE testID IN ('1', '2', '3', '200', '201')")
#query = ("SELECT kpmag, teff, dist, classif FROM minitest WHERE testID IN ('1', '2', '3', '40', '41')")
cursor.execute(query)
rows = cursor.fetchall()
rows = prep(rows)
bounds = []
print(rows)
# print(rows[1][2])
print("Hypothesis value for row 1: {}".format(h(rows[1])))
# print("Total cost value: {}".format(J(rows)))
for i in range(0, 1000):
    print("Current Theta: {}".format(theta))
    cost = J(rows)
    print("Current cost:  {} -- {} ".format(i, cost))
    # print("{},{}".format(i, cost))
    newTheta(rows, 0.01, 4)  # for 600,0,0 theta
    # newTheta(rows, 0.0021, 3) #for 0-> theta
    # newTheta(rows, 0.001, 4)
    if ((i % 15) == 1 and (i > 900)):
        bounds.append(decBound())
    if (cost == 0):
        break
print("Final theta {}".format(theta))
graph(bounds)
# for (no, dist, mag, teff, classif) in rows:
#    print("Distance: {}  \t Magnitude: {}  \t TEff: {} \t Class: {} ".format(dist, mag, teff, classif))


cursor.close()
cnx.close()
