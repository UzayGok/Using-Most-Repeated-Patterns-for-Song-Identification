
import PySimpleGUI as sg
import os
import subprocess
from random import random
from time import sleep

result = ""
# source_ https://realpython.com/pysimplegui-python/
# I changed the code a lot to fit the usage here, but that link is where I learned about this.
songname = ""
file_select_column = [                      # column to select the audio file, input.
    [
        sg.Text("Audio File"),
        sg.In(size=(25, 1), enable_events=True, key="-FILE ADDRESS-"),
        sg.FileBrowse(file_types=(("Wavesound", "*.wav"),)),
        sg.Button("Play the file", enable_events=True, key="-PLAY-")  # to play the input
    ],
    [
        
        sg.Button("Search in DB", enable_events=True, key="-SEARCH-")


    ], 
    [
        sg.Text("Song id (Necessary for DB-Inserts): "),
        sg.In(size=(25, 1), enable_events=True, key="-INPUT ID-")
    ],
    [
        sg.Text("Song name (Necessary for DB-Inserts): "),
        sg.In(size=(25, 1), enable_events=True, key="-INPUT NAME-"),

    ],
    [
        sg.Text("Artist (Necessary for DB-Inserts): "),
        sg.In(size=(25, 1), enable_events=True, key="-INPUT ARTIST-")
     ],
     [sg.Button("Insert to DB", enable_events=True, key="-INSERT-"),]

]

result_viewer_column = [  # column to view the result, output.
    [sg.Text("Result:")],
    [sg.Text(size=(40, 15), key="-TOUT-")],
    [sg.Text(key="-MATCH-")],
    [sg.Button("Play the matching song", enable_events=True, key="-RESULT-")]
]


layout = [                                  # layout of the entire window.
    [
        sg.Column(file_select_column),
        sg.VSeperator(),
        sg.Column(result_viewer_column),
    ]
]

window = sg.Window("Audio Identification", layout)
audiofile = ""
inputid = ""
inputname = ""
inputartist = ""  # to keep track of both the song id, name and its artist when inserting a song into the database
while True:
    event, values = window.read()
    if event == "Exit" or event == sg.WIN_CLOSED:
        break
    if event == "-FILE ADDRESS-":
        audiofile = values["-FILE ADDRESS-"]
        
    if event == "-INPUT ID-":
        inputid = values["-INPUT ID-"]
    if event == "-INPUT NAME-":
        inputname = values["-INPUT NAME-"]
    if event == "-INPUT ARTIST-":
        inputartist = values["-INPUT ARTIST-"]
    if event == "-INSERT-":
        if audiofile == "":
            window["-TOUT-"].update("No file was selected.")
            result=""
        elif inputid =="":
            window["-TOUT-"].update("Song id cannot be empty.")
            result=""
        else:
            # if a song is requested to be inserted into the database,
            try:
                os.rename(audiofile, str(os.path.dirname(audiofile))+"\\"+str(inputid)+".wav")    # Its name is changed to fit the playback convention, the id must match
                                                                                          # the file name, otherwise the sound file can't be found to be played. 
                audiofile= str(os.path.dirname(audiofile))+"\\"+str(inputid)+".wav"
                result=""
                window["-TOUT-"].update(os.popen("py \"insertsong.py\" " +
                                                 str(os.path.dirname(audiofile))+"\\"+str(inputid)+".wav"+" " + str(inputid) + " \""+inputname+"\" \""+inputartist+"\"").read())
            except (Exception) as error:
                window["-TOUT-"].update(error)
           
            # the related py file is called
    if event == "-SEARCH-":
        if audiofile == "":
            window["-TOUT-"].update("No file was selected.")
        else:
            try:
                result = os.popen("py \"search.py\" " + "\"" # if a song is requested to be searched for in the database,
                              # the related py file is called
                                  +audiofile+"\"").read()
                window["-TOUT-"].update(result)
                if result!="No match was found.\n":
                    result = result.split("\n")[1].split("id: ")[1]
            except (Exception) as error:
                window["-TOUT-"].update(error)
    if event == "-PLAY-":
        if audiofile == "":
            window["-TOUT-"].update("No file was selected.")
        else:
            os.startfile(audiofile)
    if event == "-RESULT-":
        cwd = os.getcwd()  # get the current directory
        # play the song in the directory, under the current implementation the UI must be in the same folder as the songs,
        if result !="" and result !="No match was found.\n":
            try:
                os.startfile(cwd+"\\"+result+".wav")
            except (Exception) as error:
                window["-TOUT-"].update(error)
        # easily changeable.


window.close()
