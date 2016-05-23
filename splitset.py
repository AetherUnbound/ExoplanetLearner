import mysql.connector

#Variable declaration space
execfile("../Login/login.py")

#SQL queries and modifications
cnx = mysql.connector.connect(**config)
cursor = cnx.cursor()
updateCursor = cnx.cursor()
m = -63.7366537882
b = 6554.99448947

for x in range(0, 555):
    query = ("SELECT * FROM trainingset2d WHERE testID='%i'" % x)
    cursor.execute(query)
    rows = cursor.fetchall()
    for (testID, origID, dist, kpmag, teff, classif, region) in rows:
        if(teff > (m*kpmag + b)): #region 1
            reg = 1
        else:
            reg = 0
        updateQuery = "UPDATE trainingset2d SET region = %s WHERE testID = '%i'" % (reg, x)
        print("Update query: %s" % updateQuery)
        updateCursor.execute(updateQuery)
        cnx.commit() #for committing changes made


cursor.close()
cnx.close()