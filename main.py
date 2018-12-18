from tkinter import *
from tkinter import filedialog
import PIL.Image
import PIL.ImageTk
from PIL import Image, ImageTk
import tkinter.messagebox
from pygame import mixer
import os
import datetime
import time
from ttkthemes import themed_tk as tk
from tkinter import ttk
import threading
import sqlite3

# initializing screen
root = tk.ThemedTk()
root.get_themes()
root.set_theme('clearlooks')
root.configure(background='white')

# initializing mixer
mixer.init()

# create menu bar
menubar = Menu(root)
root.config(menu=menubar)

# creating the list of songs, it will contain the song object (filename variable) whilst global variable only stores the name of the object
playlist = []

# creating the list for the images
imageslist = []

#creating the list for the lyrics

lyricslist = []

#creating author list
authorlist = []


# method to add image
def change_image(image):
    original = Image.open(image)
    resized = original.resize((400, 400), Image.ANTIALIAS)
    img2 = ImageTk.PhotoImage(resized)

    #img2 = ImageTk.PhotoImage(PIL.Image.open(image))

    panel.configure(image=img2)
    panel.image = img2


# method to add songs to playlist

index = 0


def add_playlist2(name, author, url, image, lyrics, extension):
    global index
    List.insert(index, name + ' - ' + author)
    playlist.insert(index, url)
    imageslist.insert(index, image)
    lyricslist.insert(index, lyrics)
    authorlist.insert(index, author)
    index += 1

#def add_text(lyrics):
    #lyricslabel.config(text=lyrics)


# method for the database data extraction
def extract_info(c):
    c.execute("SELECT * FROM Songs")
    results = c.fetchall()
    global name
    global author
    global url
    global image
    global lyrics
    global extension

    for i in results:
        name = i[1]
        author = i[2]
        url = i[3]
        image = i[4]
        lyrics = i[5]
        extension = i[6]
        add_playlist2(name, author, url, image, lyrics, extension)


# browse file method
def browse_file():
    global filename
    global c
    filename = filedialog.askopenfilename()
    variable = os.path.splitext(filename)[1]
    if variable == ".db":
        conn = sqlite3.connect(filename)
        c = conn.cursor()
        extract_info(c)
    elif variable == ".wav":
        variable = os.path.basename(filename)
        add_playlist(filename)
    else:
        tkinter.messagebox.showerror('Error 800', 'Invalid selected file. Choose a .db or .wav.')


index = 0


# creating add to playlist function
def add_playlist(filename):
    global variable
    global index
    variable = os.path.basename(filename)
    List.insert(index, variable)
    playlist.insert(index, filename)
    index += 1


# create a submenu

submenubar = Menu(menubar, tearoff=0)
menubar.add_cascade(label='File', menu=submenubar)
submenubar.add_command(label="Open", command=browse_file)
submenubar.add_command(label="Exit", command=root.destroy)  # root.destroy is a command used to kill the program.


# about us method
def about_us():
    tkinter.messagebox.showinfo('Playable',
                                'Copyright on content: Charly 2018, all rights reserved.')  # message that will displayed at the About us window


submenubar = Menu(menubar, tearoff=0)
menubar.add_cascade(label='Help', menu=submenubar)
submenubar.add_command(label="About Us", command=about_us)

# giving the dimensions to the screen.
#root.geometry('800x814')

# adding a title to the program.
root.title('Playable')

# adding an icon next to the title. Works in windows, mac seems it does not work properly.
root.iconbitmap(r'Static/logo.ico')

# status bar
statusbar = Label(root, text='Playable', relief=SUNKEN, anchor=W)
statusbar.pack(side=BOTTOM, fill=X)

# dividing window into right and left
rightframe = Frame(root)
rightframe.pack(side=RIGHT, padx=10)

leftframe = Frame(root)
leftframe.pack(side=LEFT, padx=30)

middleframe = Frame(root)
middleframe.pack(padx=10)
# dividing the window into two general framses (up and down). Up frame will be for the playlist and down for the play, stop, mute...
upframe = Frame(middleframe)
upframe.pack()

downframe = Frame(middleframe)
downframe.pack()

# importing logo
img = ImageTk.PhotoImage(PIL.Image.open("Static/playable400.png"))
panel = Label(upframe, image=img)
panel.pack(side=TOP, pady=10)

# creating a list of songs (window) (left frame)
List = Listbox(leftframe)
List.config(width=30, height=37)
List.pack(padx=10, pady=10)

# creating add or delete song
add = ttk.Button(leftframe, text='+Add', command=browse_file)
add.place(relx=0.5, rely=0.5, anchor=CENTER)
add.pack(side=LEFT, pady=5)

# delete song method
def delete_song():
    selected_song = List.curselection()
    selected_song = int(selected_song[0])
    List.delete(selected_song)
    playlist.pop(selected_song)


delete = ttk.Button(leftframe, text='-Delete', command=delete_song)
delete.place(relx=0.5, rely=0.5, anchor=CENTER)
delete.pack(side=RIGHT, pady=5)

# adding some text inside the window.
filetext = Label(upframe, text='Playing: ----:----', pady=10)
# it is necesary to add text.pack after each label in order to keep working properly the program.
filetext.pack()

# adding the top frame for the downframe
topdownframe = Frame(downframe)
topdownframe.pack()

# adding length of the song
lengthlabel = Label(topdownframe, text='Total Length - --:--')
lengthlabel.pack(pady=10)

# adding length of the song
currentimelabel = Label(topdownframe, text='Current Time - --:--', relief=GROOVE)
currentimelabel.pack()

#method to add the author info, once the user click play button.
def create_detail2(t):
    global authorlabel
    authorlabel = Label(upframe, text='Artist: '+ authorlist[t], relief=GROOVE)
    authorlabel.pack()

def change_detail2(t):
    authorlabel.config(text='Artist: ' + authorlist[t])

# creation of length method
def detail():
    info = os.path.basename(play_it)
    filetext.config(text='Playing: ' + info)

    a = mixer.Sound(play_it)
    total_length = a.get_length()
    timeformat = str(datetime.timedelta(round(total_length) / 86400))

    lengthlabel.config(text='Total Length: ' + timeformat)

    # following t1 lines is for showing the counter at the player.
    t1 = threading.Thread(target=start_count, args=(total_length,))
    t1.start()


def start_count(t):
    global paused
    global x
    global timeformat
    x = 0
    timeformat = 0

    while x <= t and mixer.music.get_busy():
        if paused:
            continue
        else:

            timeformat = str(datetime.timedelta(round(x) / 86400))
            currentimelabel.config(text='Current Time: ' + timeformat, foreground='red')
            x += 1
            time.sleep(1)


# know which song is playing (right side)
flag = TRUE
flag2 = TRUE
def create_lyrics(t):

    global lyrics
    lyrics = Text(rightframe, height=45, width=65)    # from tkinter
    S = Scrollbar(rightframe)
    S.pack(side=RIGHT, fill=Y)
    lyrics.pack(side=LEFT, fill=Y)
    S.config(command=lyrics.yview)
    lyrics.config(yscrollcommand=S.set)
    lyrics.insert(END, 'LYRICS\n\n'+lyricslist[t])
    lyrics.tag_configure("center", justify='center')
    lyrics.tag_add("center", '1.0', END)
    #lyrics = Label(rightframe, text=lyricslist[t])
    #lyrics.pack()


def change_lyrics(t):
    lyrics.delete('1.0', END)
    lyrics.insert(END, 'LYRICS\n\n'+lyricslist[t])
    lyrics.tag_configure("center", justify='center')
    lyrics.tag_add("center", '1.0', END)



def play_btn():
    global flag  # declare play btn, lists, boolean pause
    global flag2
    global paused
    global play_it
    global counter
    global x

    if paused:
        mixer.music.unpause() #paused and unpause music
        paused = FALSE

    else:
        try:                                       #first time user clicks play
            selected_song = List.curselection()  #parse index of the song
            selected_image = int(selected_song[0]) #selected on the list by the curse
            selected_song = int(selected_song[0])
            play_it = playlist[selected_song]
            change_image(imageslist[selected_image])
            mixer.music.load(play_it)
            mixer.music.play()
            detail()
            if flag:
                create_lyrics(selected_image)
                flag = FALSE
            else:
                change_lyrics(selected_image)

            if flag2:
                create_detail2(selected_image)
                flag2 = FALSE
            else:
                change_detail2(selected_image)


        except:
            tkinter.messagebox.showerror('Error 404', 'None selected file.')




def rewind_btn():
    mixer.music.stop()
    mixer.music.load(play_it)
    mixer.music.play()
    start_count(0)



paused = FALSE


def pause_btn():
    global paused
    paused = TRUE
    mixer.music.pause()


def stop_btn():
    mixer.music.stop()


def set_vol(val):
    volume = float(
        val) / 100  # divided by 100 because mixer only accept values from 0 to 1. As we have asigned at the volume scale
    mixer.music.set_volume(volume)


muted = FALSE


def mute_music():
    global muted
    if muted:  # if true unmute the music
        muted = FALSE
        mixer.music.set_volume(0.7)
        volumeBtn.configure(image=volumePhoto)
        scale.set(70)
    else:  # if false mute the music
        muted = TRUE
        mixer.music.set_volume(0)
        volumeBtn.configure(image=mutePhoto)
        scale.set(0)


# isolating play, pause, stop buttons in a frame.
middleframe = Frame(downframe)
middleframe.pack(padx=10, pady=10)

# Get pause image and convert it into a button.
stopphoto = ImageTk.PhotoImage(PIL.Image.open('Static/stop.png'))
stop_btn = Button(middleframe, image=stopphoto, command=stop_btn)
stop_btn.grid(row=0, column=3, padx=10)

# Get the play image and convert it into a button
playphoto = ImageTk.PhotoImage(PIL.Image.open('Static/play.png'))
play_btn = Button(middleframe, image=playphoto, command=play_btn)
play_btn.grid(row=0, column=1, padx=10)

# Get stop image and convert it into a button.
pausephoto = ImageTk.PhotoImage(PIL.Image.open('Static/pause.png'))
pause_btn = Button(middleframe, image=pausephoto, command=pause_btn)
pause_btn.grid(row=0, column=2, padx=10)

# Get rewind image and convert it into a button.
rewindphoto = ImageTk.PhotoImage(PIL.Image.open('Static/rewind.png'))
rewind_btn = Button(middleframe, image=rewindphoto, command=rewind_btn)
rewind_btn.grid(row=0, column=0, padx=10)

# isolating scale bar and volume/mute button.
bottomframe = Frame(downframe)
bottomframe.pack()

# create volume and mute button (bottom from down frame)
mutePhoto = ImageTk.PhotoImage(PIL.Image.open('Static/mute.png'))
volumePhoto = ImageTk.PhotoImage(PIL.Image.open('Static/volume.png'))
volumeBtn = Button(bottomframe, image=volumePhoto, command=mute_music)
volumeBtn.grid(row=0, column=0, padx=10)

# creating control volume scale
scale = Scale(bottomframe, from_=0, to=100, orient=HORIZONTAL, command=set_vol)
scale.set(70)  # setting the volume control at 70 as a defaul value
mixer.music.set_volume(0.7)  # setting the volume at 0.7 as a defaul value
scale.grid(row=0, column=1, padx=10)

# method for the on closing error
def on_closing():
    mixer.music.stop()
    root.destroy()


# avoid close error while listening to music
root.protocol("WM_DELETE_WINDOW", on_closing)
root.mainloop()

root.mainloop()
