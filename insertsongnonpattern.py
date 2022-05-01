import xml.etree.ElementTree as ET
import librosa
import numpy as np
import sys
import os
import psycopg2
from constants import notes, params
from functions import is_slice_in_list, extract, findNotes, generateFingerprint, finger_to_str, datasplitter


audio_path = "./" + str(sys.argv[1])+".wav"

#fingerprint: 2 dimensional array containing the list representing every frame wherein the frequency value, the primary note and the secondary note are stored.
def insertrow(fingerprint):   # Inserts one row into the database. The row has the id, name, artist, primary notes, secondary notes, frequency values and the first
    # couple notes of the primary notes column.
    try:
        conn = psycopg2.connect(params)
        cur = conn.cursor()
        fingerray = finger_to_str(fingerprint)
        postgres_insert_query = """ INSERT INTO songsnonpattern (id, name, artist, primnote, secnote, freqval, firstnotes) VALUES (%s,%s,%s,%s,%s,%s,%s)"""
        
        record_to_insert = (os.path.basename(sys.argv[1]).split(".")[0], '-',
                            '-', fingerray[1], fingerray[2], fingerray[0], fingerprint[0][1]+","+fingerprint[1][1])
        cur.execute(postgres_insert_query, record_to_insert)

        conn.commit()
        count = cur.rowcount
        print(str(count), "Row inserted successfully into the database.")
    except (Exception, psycopg2.Error) as error:
        print("Failed to insert record into the database.", error)
    finally:
        # closing database connection.
        if conn:
            cur.close()
            conn.close()
            print("PostgreSQL connection is closed.")
#source: https://pynative.com/python-postgresql-insert-update-delete-table-data-to-perform-crud-operations/#h-python-postgresql-insert-into-database-table
#taken from the source, altered to fit the usage.


#-------------


try:
    x, sr = librosa.load(audio_path, sr=16000)
except (Exception) as error:
    print(error) 
Nfft = 4096
y = librosa.fft_frequencies(sr=sr, n_fft=Nfft)

X = librosa.stft(x, n_fft=Nfft)
Xdb = librosa.amplitude_to_db(abs(X))

chromaList = extract( Xdb, y, notes)
primaryNotes, secondaryNotes = findNotes(chromaList)

fingerprint = generateFingerprint(primaryNotes, secondaryNotes, Xdb)

insertrow(fingerprint)


