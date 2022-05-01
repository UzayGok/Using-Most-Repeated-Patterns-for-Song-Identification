import psycopg2
import os
from constants import params


#source: https://www.postgresqltutorial.com/postgresql-python/create-tables/
# I took the code and changed it a little to fit the usage here.
def create_table(): #no arguments, creates a table in the database with columns fitting the format seen below.
    command = """ CREATE TABLE songsnonpatterntwo (id SERIAL PRIMARY KEY, name VARCHAR(255) NOT NULL, artist VARCHAR(255) NOT NULL, 
    primnote TEXT NOT NULL, secnote TEXT NOT NULL, freqval TEXT NOT NULL, firstnotes TEXT NOT NULL)"""
    try:
        conn = psycopg2.connect(params)
        cur = conn.cursor()
        cur.execute(command)
        cur.close()
        conn.commit()
        print("Table CREATED")
    except (Exception, psycopg2.DatabaseError) as error:
        print(error)
    finally:
        if conn is not None:
            conn.close()


if __name__ == '__main__':
    create_table()
#source: https://www.postgresqltutorial.com/postgresql-python/create-tables/

#------

#for i in range(25, 77):                          #This was the earlier usage to start the database. This has been deprecated since the implementation of the UI.
 #   os.system("py \"insertsong.py\" "+str(i)+ " - -")


#The rest is to be disregarded. It was for the previous database.

#import xml.etree.ElementTree as ET
# tree=ET.parse("database.xml")
# root=tree.getroot()
# print(root[0][32].attrib)
# for i in range(0, 3):
  #  for j in range(1, 13):
    #    print(str(i+(j-1)/12)+" & "+str(notes[i][j])+"         \\\\")       #+str(261.63*(2**(i+(j-1)/12)))+"     \\\\")
