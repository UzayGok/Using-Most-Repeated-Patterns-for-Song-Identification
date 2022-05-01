from datetime import datetime

def is_slice_in_list(s, l):
    len_s = len(s) 
    return any(s == l[i:len_s+i] for i in range(len(l) - len_s+1)) 
#source: https://stackoverflow.com/questions/20789412/check-if-all-elements-of-one-array-is-in-another-array 
#stackoverflow - directlink to answer: https://stackoverflow.com/a/20789669

def printmatrix(mat):  # This was used for testing at earlier stages of development. Takes a two dimensional list, no return value. Prints the matrix to the terminal 
                       # with a basic layout
    for i in range(len(mat)):
        line = ""
        for ii in range(len(mat[i])):
            line += str(mat[i][ii])+"|"
        print(line)

    # audio_path:string for path to the audio file, Xdb: two dimensional list, frames on one axis frequency values on the other, amplitude in dB as values (float).
def extract( Xdb, y, notes):    #This function essentially returns a list of chroma vectors representing every frame.
    # "amps" is the temporary vector that stores the current chroma vector at every iteration and 
    # once the frame is completely inspected it gets appended to the chromaList vector.


    chromaList = []

    for xx in range(0, len(Xdb[0])):
        amps = [0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0]

        for i in range(0, 3):
            for j in range(1, 13):
                templow = 0
                tempk = 0

                for k in range(0, len(y)):
                    if(y[k] <= notes[i][j] and notes[i][j]-y[k] < notes[i][j]-templow):
                        templow = y[k]
                        tempk = k
                    elif(y[k] >= notes[i][j]):
                        ttemp = (((1-(notes[i][j]-y[tempk])/(notes[i][j]-notes[i][j-1])))*Xdb[tempk][xx] + (
                            (1-(y[k]-notes[i][j])/(notes[i][j+1]-notes[i][j])))*Xdb[k][xx])*(1+0.156*(1/2**(i+(j-1)/12))) 
                            # The calculation here takes the weighted (by difference in cents) average 
                            # of the amplitude value present at the two closest frequency values to every note, which is then multiplied by a function 
                            # to make up for the fact that fft frequencies have less difference in cents to higher notes than lower ones. The calculation is not exact, 
                            # but in relation to the computational time and accuracy of the results it is good enough. More will be explained
                            # in the related section.  
                        if (ttemp >= 0):
                            amps[j-1] += ttemp
                        break
        chromaList.append(amps)
    return chromaList

def printTime(message):         # meesage:string, prints the time in format [message]" "["%H:%M:%S:%f"] into the terminal.
    now = datetime.now()
    current_time = now.strftime("%d.%m.%Y %H:%M:%S,%f")  #used to print directly into the terminal, hence the naming
    return message + str(current_time)

#Takes the two dimensional list of chroma vectors (float list), each representing a single frame.
def findNotes(chromaList):    # This function takes the list with all the chroma vectors and simply finds out the first and second highest amplitude notes.
    primaryNotes = []
    secondaryNotes = []
    for i in range(0, len(chromaList)):
        primNoteIndex = 0
        secNoteIndex = 1
   
   # if(i < 100):                 #This was for testing on the spot during early development.
    #  print("C: "+str(chromaList[i][0])+", C#: "+str(chromaList[i][1])+", D: "+str(chromaList[i][2])+", Eb: "+str(chromaList[i][3])+", E: "+str(chromaList[i][4])+", F: " + str(chromaList[i][5]) +
    #  ", F#: "+str(chromaList[i][6])+", G: "+str(chromaList[i][7])+", G#: "+str(chromaList[i][8])+", A: "+str(chromaList[i][9])+", Bb: "+str(chromaList[i][10])+", B: "+str(chromaList[i][11])+"\n")
        for ii in range(1, len(chromaList[0])):

            if chromaList[i][ii] > chromaList[i][primNoteIndex]:
                secNoteIndex = primNoteIndex
                primNoteIndex = ii
            elif chromaList[i][ii] > chromaList[i][secNoteIndex]:
                secNoteIndex = ii

        if chromaList[i][primNoteIndex] > 9.99:       # This step is crucial, because thanks to this step frames with barely 
                                                      # any sound (usually frames that are completely silent) are left out
                                                      # to avoid matching songs due to a similar duration of silence.
            primaryNotes.append(primNoteIndex+1)
            secondaryNotes.append(secNoteIndex+1)
    return primaryNotes, secondaryNotes

#primaryNotes: int list, secondaryNotes: int list, Xdb: two dimensional list, frames on one axis frequency values on the other, amplitude in dB as values (float).
def generateFingerprint(primaryNotes, secondaryNotes, Xdb):  # This function generates the fingerprint list for given data.
    fingerprint=[]
    i2 = 0
    while(i2 < len(primaryNotes)-1):
        temphigh = 77    # The frequency value with the highest amplitude of the frame i2
        temphigh2 = 77   # The frequency value with the highest amplitude of the frame i2+1
        for ii in range(78, 537): # The choice of the interval [77, 537] is due to it representing the frequency range that this project revolves around.
            if Xdb[ii][i2] > Xdb[temphigh][i2]:
                temphigh = ii
        for ii in range(78, 537):
            if Xdb[ii][i2+1] > Xdb[temphigh][i2+1]:
                temphigh2 = ii
        fingerprint.append([str(round((temphigh+temphigh2)/2)), # This step combines frames 1 and 2, 3 and 4, 5 and 6, ... to increase efficiency and also helps to
                                                                # eliminate coincidental singular note/ frequency matches to cause false positives.
                                                                # The index of the frequency value instead of the value itself is stored to decrease the needed storage,
                                                                # because the considered frequencies are 3 to 4 digits whereas the indeces are strictly 3 digits.

                        str(primaryNotes[i2]+primaryNotes[i2+1]*100), str(secondaryNotes[i2]+secondaryNotes[i2+1]*100)]) 
                        # The notes are stored as C=1, C#=2, ..., B=12,
                        # therefore "secondaryNotes[i2]+secondaryNotes[i2+1]*100"
                        # uniquely maps the notes to a combination of two frames.
        i2 += 2
    return fingerprint

#list_of_Notes: two dimensional list, every single list is in format [int,int,int], contains the frequency value, primary note and secondary note for every frame
def finger_to_str(list_of_Notes):
    result1 = str(list_of_Notes[0][0])
    result2 = str(list_of_Notes[0][1])
    result3 = str(list_of_Notes[0][2])
    for i in range(1, len(list_of_Notes)):
        result1 += ","+str(list_of_Notes[i][0])
        result2 += ","+str(list_of_Notes[i][1])
        result3 += ","+str(list_of_Notes[i][2])
    return [result1, result2, result3]

#dstr: str
def datasplitter(dstr):    # Data is stored as text in the postgresql database, with comma in between every piece of information. 
                           # This function converts the text data into an array for comparison purposes. This is a trivial function under the current circumstances,
                           # but will be kept and used in case the way data is stored in the database changes, because this function would then make it easier to adapt
                           # the code to the changes.
    dstr = dstr.split(",")
    return dstr