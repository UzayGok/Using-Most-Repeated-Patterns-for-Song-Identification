# the call to this is py insertsong.py [path to audio] [id] [name] [artist]

import psycopg2
import librosa
import numpy as np
import sys
import os
audio_path = str(sys.argv[1])
from functions import is_slice_in_list, printmatrix, extract, findNotes, finger_to_str, generateFingerprint
from constants import notes, params

#primaryNotes: int list
def generateMatrix(primaryNotes):      #compares the primary notes array to itself (at different starting positions) to build a triangular matrix where diagonals of sequential 1s mean there is a repetition.
    matrix = []

    for i in range(0, len(primaryNotes)):
        matrix.append([])
        for ii in range(0, i):
            if(primaryNotes[i] == primaryNotes[ii]):
                matrix[i].append(1)
            else:
                matrix[i].append(0)
    return matrix
# matrix: two dimensional array of 1s and 0s (int), primaryNotes: int list, secondaryNotes: int list.
def find_diagonals(matrix, primaryNotes, secondaryNotes):
    patterns2 = []        # Keeps track of the secondary notes of every pattern found so far. Although not yet functionally necessary, will be so in the next few functions.
    patterns = []         # Keeps track of the primary notes of every pattern found so far.
    startss = []          # Keeps track of the starting positions of every pattern. The starting position refers to the index in the frames array representing the whole song. Necessary for the contuniation of the
                          # functionality.
    for i in range(1, len(matrix)):
        for ii in range(0, len(matrix[i])):             #two dimensional array, matrix.
            if(matrix[i][ii] == 1):
                score = [1, 1]
                tempi = i                   #temporarily keeps the value of i, necessary for finding diagonals
                tempii = ii                 #temporarily keeps the value of ii
                pattern = [primaryNotes[i]]        #keeps track of the primary notes for every frame present in a pattern
                pattern2 = [secondaryNotes[i]]      #keeps track of the secondary notes for every frame present in a pattern
                while(score[0]/score[1] >= 0.74):  # The percentage of matching notes. Logically this would imply that the first 3 notes must match for a pattern to be surveyed, which makes sense because 
                                                   # a start with a high percentage of match means that the chances are higher for a meaningful diagonal to be found, which saves the computational cost of traversing
                                                   # with the hope of finding a pattern where there is possibly none. The frames have a large overlap, so the first 3 frames should match for most of the repetitions
                                                   # anyway.
                    tempi += 1
                    tempii += 1
                    if(tempi >= len(matrix) or tempii >= len(matrix[tempi])):  # To not traverse beyond the matrix boundaries.
                        break
                    score[0] += matrix[tempi][tempii]                   # score[0] only gets incremented when the matrix has a 1 on that spot, whereas score[1] keeps track of the number of traversed frames.
                    score[1] += 1
                    pattern.append(primaryNotes[tempi])      
                    pattern2.append(secondaryNotes[tempi])
                if(len(pattern) >= 20):  # min pattern length in frames
                    patterns.append(pattern)
                    patterns2.append(pattern2)
                    startss.append(i)
                    for iii in range(1, (tempii-ii)+1):           # replaces the 1s with 0s after a pattern is found and completely traversed.
                        matrix[tempi-iii][tempii-iii] = 0
    return patterns, patterns2, startss

#fingerprint: 2 dimensional array containing the list representing every frame wherein the frequency value, the primary note and the secondary note are stored.
def insertrow(fingerprint):  # Inserts one row into the database. The row has the id, name, artist, primary notes, secondary notes, frequency values and the first
    # couple notes of the primary notes column.
    try:
        conn = psycopg2.connect(params)
        cur = conn.cursor()
        fingerray = finger_to_str(fingerprint)
        postgres_insert_query = """ INSERT INTO songs (id, name, artist, primnote, secnote, freqval, firstnotes) VALUES (%s,%s,%s,%s,%s,%s,%s)"""
        
        record_to_insert = (sys.argv[2], sys.argv[3],
                            sys.argv[4], fingerray[1], fingerray[2], fingerray[0], fingerprint[0][1]+","+fingerprint[1][1])
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

#----------
try:
    x, sr = librosa.load(audio_path, sr=16000)
except (Exception) as error:
    print(error) 


Nfft = 4096
y = librosa.fft_frequencies(sr=sr, n_fft=Nfft)

X = librosa.stft(x, n_fft=Nfft)
Xdb = librosa.amplitude_to_db(abs(X))

chromaList = extract(Xdb, y, notes)
primaryNotes, secondaryNotes = findNotes(chromaList)
matrix=generateMatrix(primaryNotes)


patterns, patterns2, startss = find_diagonals(matrix,primaryNotes,secondaryNotes)

repeats = []
for i in range(0, len(patterns)):      # This code here calculates, for each pattern; the sum of the count of repetitions of itself, the number of other patterns that contain it and the number of
                                       # patterns that it contains.
    repeats.append(1)
    ii = i+1
    while(ii < len(patterns)):
        if patterns[i] == patterns[ii] or is_slice_in_list(patterns[ii], patterns[i]) or is_slice_in_list(patterns[i], patterns[ii]):  
            repeats[i] += 1                 # This code here pops patterns that have already been counted. It functionally prefers repetitions of patterns that are closer to the start of a song. 
                                            # The assumption here is that sections closer to the beginning are more memorable and that the user would search for the song right after hearing it and deciding
                                            # that they like it, making it likelier that repetitions closer to the beginning will be subject to queries.
            patterns.pop(ii)
            patterns2.pop(ii)
            startss.pop(ii)
        ii += 1

maxrep = 0
for i in range(1, len(repeats)):
    if repeats[i] > repeats[maxrep]:        # The pattern with the highest sum is discovered.
        maxrep = i


fingerprint = []
i2=startss[maxrep]
end=startss[maxrep]+120
if(len(primaryNotes)-startss[maxrep]<120):
    i2=startss[maxrep]-(120-(len(primaryNotes)-startss[maxrep]))    # The number of frames is limited/ completed to 120. If the pattern is longer, first 120 frames are recorded. If the pattern is shorter,
    end=i2+120                                                      # the following frames are added to the fingerprint. If the pattern is too close to the end of the song, not leaving enough frames to
if(i2<0):                                                           # satisfy 120, frames before the starting point are added. The pattern being too close to the end of the song is presumably not very healthy,
                                                                    # given the likelihood of the user inputting the very end of the song and the endings usually not perfectly resembling the rest of the song.
                                                                    # Therefore, no matter the length of the pattern and the number of remaining frames, if there are not enough frames until the end all of them
                                                                    # are discarded and instead the prior frames are taken into account.
                                                                    
    i2=0
primaryNotes=primaryNotes[i2:end]
secondaryNotes=secondaryNotes[i2:end]
Xdb=Xdb[0:,i2:end]
fingerprint= generateFingerprint(primaryNotes, secondaryNotes, Xdb)


insertrow(fingerprint)


#TO BE DISREGARDED

#file1 = open("database.xml", "a")
# file1.write("<item fingerprint=\""+str(hash(finger_to_str(fingerprint))) +
 #           "\" id=\""+str(sys.argv[1])+"\">"+str(sys.argv[1])+"song</item>")

#import xml.etree.ElementTree as ET
# data=ET.parse("database.xml")
