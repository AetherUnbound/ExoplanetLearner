import mysql.connector

#Variable declaration space
config = {
    'user': 'bowdenm',
    'password': 'dinglebrumbus',
    'host': 'cs.spu.edu',
    'database': 'bowdenm_exoplanet',
    'raise_on_warnings': True
}

classDict = {
    'M' : {'base':  2400, 'range':  1300},
    'K' : {'base':  3700, 'range':  1500},
    'G' : {'base':  5200, 'range':   800},
    'F' : {'base':  6000, 'range':  1500},
    'A' : {'base':  7500, 'range':  2500},
    'B' : {'base': 10000, 'range': 20000},
    'O' : {'base': 30000, 'range': 30000},
}

#Function declaration space
def getTEFF(specClass):
    #specClass will be a 2 char string of the form [A-Z][0-9]
    #Equation: teff = base + rangePortion
    #          teff = base + (range * (10-Num)/10)
    #   This allows 0 to be the hottest and 9 to be the coolest
    #   Inputs do not need verification as database is sanitized
    classification = classDict[specClass[0]]
    teff = (classification['base'] + (classification['range']*((10-float(specClass[1]))/10)))
    return teff


#SQL queries and modifications
cnx = mysql.connector.connect(**config)
cursor = cnx.cursor()
updateCursor = cnx.cursor()

for x in range(119613, 119614):
    query = ("SELECT * FROM hygset WHERE id='%i'" % x)
    cursor.execute(query)
    rows = cursor.fetchall()
    for (id, dist, mag, absmag, spect, ci, lum, teff) in rows:
        newTeff = str(getTEFF(spect))
        print("RowID: {} \t Distance: {} \t Spectral class: {}  ".format(id, dist, spect[:2]) + "  Calculated temperatre: "+ newTeff)
        updateQuery = "UPDATE hygset SET teff = %s, spect = '%s' WHERE id = '%i'" % (newTeff, spect[:2], id)
        print("Update query: %s" % updateQuery)
        updateCursor.execute(updateQuery)
        cnx.commit() #for committing changes made


cursor.close()
cnx.close()