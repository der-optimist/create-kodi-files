# -*- coding: utf-8 -*-
import tkinter as tk
import tkinter.filedialog
from PIL import ImageTk, Image
import os, os.path, time
from shutil import copy, move
import cv2
from subprocess import check_output
import codecs

# Input
filetype = ".mp4"

class MainWindow():
    def __init__(self, root, filetype):
        # define global vars
        self.filetype = filetype
        self.list_files = []
        self.list_titles = []
        self.list_embarrassing = []
        self.current_index = 0
        # define tkinter variables
        self.folder_path = tk.StringVar()
        self.var_fanart = tk.IntVar()
        self.var_poster1 = tk.IntVar()
        self.var_poster2 = tk.IntVar()
        self.text_curr_page = tk.StringVar()
        self.text_curr_page.set("Bitte Ordner wählen")
        self.var_embarr = tk.IntVar()
        self.folder_path.set("Bitte Ordner mit den Video-Dateien auswählen")
        self.text_status = tk.StringVar()
        # create window top area
        self.create_window_top()
        # create window main area
        self.create_window_main()
        # create window bottom area
        self.create_window_bottom()
        
    def get_files(self, folder, filetype):
        self.list_paths = []
        self.list_filenames = []
        self.list_dir = os.listdir(folder)
        for file in self.list_dir:
            if file.endswith(filetype):
                file_path = os.path.normpath(os.path.join(folder, file))
                self.list_paths.append(file_path)
                self.list_filenames.append(file)
        return self.list_paths
    
    def init_var_lists(self, list_files):
        self.list_titles = [''] * len(list_files)
        self.list_embarrassing = [0] * len(list_files)
        self.list_fanart = [4] * len(list_files)
        self.list_poster1 = [1] * len(list_files)
        self.list_poster2 = [7] * len(list_files)
    
    def update_page(self, index):
        self.var_fanart.set(self.list_fanart[index])
        self.var_poster1.set(self.list_poster1[index])
        self.var_poster2.set(self.list_poster2[index])
        self.entry_title.delete(0, tk.END)
        self.entry_title.insert(0, self.list_titles[index])
        self.var_embarr.set(self.list_embarrassing[index])
        self.text_curr_page.set("Film " + str(self.current_index + 1) + " von " + str(len(self.list_files)))
        self.load_frames(index)
    
    def load_frames(self, index):
        self.list_frames = [Image.new('RGB', (self.imagewidth,self.canvasheight), (0, 0, 0))] * 9
        if len(self.list_files) > 0:
            for i in range(9):
                name_frame = self.list_files[index][:-4] + '_frame0' + str(i+1) + '.jpg'
                img = Image.open(name_frame)
                size = self.imagewidth, int(self.imagewidth*img.size[1]/img.size[0])
                self.list_frames[i] = img.resize(size, Image.ANTIALIAS)
        self.list_images_tk = []
        for i in range(9):
            self.list_images_tk.append(ImageTk.PhotoImage(self.list_frames[i]))
            self.list_canvas[i].create_image(0, 0, anchor = tk.NW, image = self.list_images_tk[i])

    def extract_frames(self, video_file):
        # video screenshots
        # check if they already exist
        all_frames_exist = True
        for i in range(1,10):
            name_frame = video_file[:-len(self.filetype)] + '_frame0' + str(i) + '.jpg'
            if not os.path.isfile(name_frame):
                all_frames_exist = False
        if not all_frames_exist:
            frames = self.count_frames(video_file)
            name_frames = video_file[:-4] + '_frame%02d.jpg'
            check_output(['ffmpeg', '-i', video_file, '-vf', 'thumbnail=' + str(round(frames/9)) + ',setpts=N/TB', '-r', '1', '-vframes', '9', name_frames])
            #out = check_output(['ffmpeg', '-i', video_file, '-vf', 'thumbnail=' + str(round(frames/9)) + ',setpts=N/TB', '-r', '1', '-vframes', '9', name_frames])
            #print(out)
    
    def save_current_values(self):
        self.list_titles[self.current_index] = self.entry_title.get()
        self.list_embarrassing[self.current_index] = self.var_embarr.get()
        self.list_fanart[self.current_index] = self.var_fanart.get()
        self.list_poster1[self.current_index] = self.var_poster1.get()
        self.list_poster2[self.current_index] = self.var_poster2.get()
    
    def update_directory(self):
        self.folder = tk.filedialog.askdirectory()
        self.folder_path.set(self.folder)
        self.list_files = self.get_files(self.folder_path.get(), self.filetype)
        if len(self.list_files) > 0:
            self.init_var_lists(self.list_files)
            self.text_curr_page.set("Erstelle Bilder")
            for i in range(len(self.list_files)):
                self.text_status.set("Erstelle Bilder (Film " + str(i + 1) + " von " + str(len(self.list_files)) + ")")
                root.update()
                self.extract_frames(self.list_files[i])
                self.text_status.set("Bilder von allen Filmen erstellt => es kann los gehen ✔️")
            self.current_index = 0
            self.update_page(self.current_index)
        else:
            self.text_status.set("Gewählter Ordner enthält keine entsprechenden Videos")
        root.bind("<Return>", self.goto_next)
    
    def goto_next(self, _event=None):
        self.save_current_values()
        if self.current_index < (len(self.list_files) - 1):
            self.current_index += 1
        self.update_page(self.current_index)
    
    def goto_prev(self):
        self.save_current_values()
        if self.current_index > 0:
            self.current_index -= 1
        self.update_page(self.current_index)
    
    def count_frames(self, video_filename):
        cap = cv2.VideoCapture(video_filename)
        video_length = int(cap.get(cv2.CAP_PROP_FRAME_COUNT)) - 1
        if cap.isOpened():
            cap.release()
        return video_length
    
    def work(self):
        self.save_current_values()
        self.folder_backup_audio = tk.filedialog.askdirectory(title = "Ordner für Audio-Backups wählen")
        for i in range(len(self.list_files)):
            if self.list_titles[i] != '':
                # save timestamp of video file
                stat = os.stat(self.list_files[i])
                # backup of the original audio stream
                backup_path = os.path.normpath(os.path.join(self.folder_backup_audio, self.list_filenames[i]))
                self.text_status.set("Film " + str(i + 1) + " von " + str(len(self.list_files)) + ": Erstelle Audio-Backup")
                root.update()
                check_output(['ffmpeg', '-i', self.list_files[i], '-vn', '-acodec', 'copy', backup_path])
                os.utime(backup_path, (stat.st_atime,stat.st_mtime))
                self.text_status.set("Film " + str(i + 1) + " von " + str(len(self.list_files)) + ": Gleiche Lautstärke an (\"normalisiere\")")
                root.update()
                # normalize audio volume
                check_output(['ffmpeg-normalize', '-v', self.list_files[i], '-c:a', 'aac', '-b:a', '192k', '-ar', '48000', '-o', self.list_files[i], '-f'])
                os.utime(self.list_files[i], (stat.st_atime,stat.st_mtime))
                # rename fanart
                frame_fanart = self.list_files[i][:-len(self.filetype)] + '_frame0' + str(self.list_fanart[i] + 1) + '.jpg'
                copy(frame_fanart, self.list_files[i][:-len(self.filetype)] + '-fanart.jpg')
                # combine poster1 and poster2 to poster
                poster = Image.new('RGB', (954,1080), (0, 0, 0))
                poster1 = Image.open(self.list_files[i][:-len(self.filetype)] + '_frame0' + str(self.list_poster1[i] + 1) + '.jpg')
                poster2 = Image.open(self.list_files[i][:-len(self.filetype)] + '_frame0' + str(self.list_poster2[i] + 1) + '.jpg')
                size = 938, int(938*poster1.size[1]/poster1.size[0])
                poster1 = poster1.resize(size, Image.ANTIALIAS)
                poster2 = poster2.resize(size, Image.ANTIALIAS)
                poster.paste(poster1, (8, 8, 946, 8 + size[1]))
                poster.paste(poster2, (8, 544, 946, 544 + size[1]))
                poster.save(self.list_files[i][:-len(self.filetype)] + '-poster.jpg')
                # create nfo file
                self.create_nfo(self.list_files[i], stat.st_mtime, self.list_titles[i], self.list_embarrassing[i])
                # move kodi files to subfolder
                basename = self.list_filenames[i][:-len(self.filetype)]
                subfolder = os.path.normpath(os.path.join(self.folder,basename))
                try:
                    os.stat(subfolder)
                except:
                    os.mkdir(subfolder)
                move(os.path.normpath(os.path.join(self.folder,basename + self.filetype)),os.path.normpath(os.path.join(self.folder,basename,basename + self.filetype)))
                move(os.path.normpath(os.path.join(self.folder,basename + '-fanart.jpg')),os.path.normpath(os.path.join(self.folder,basename,basename + '-fanart.jpg')))
                move(os.path.normpath(os.path.join(self.folder,basename + '-poster.jpg')),os.path.normpath(os.path.join(self.folder,basename,basename + '-poster.jpg')))
                move(os.path.normpath(os.path.join(self.folder,basename + '.nfo')),os.path.normpath(os.path.join(self.folder,basename,basename + '.nfo')))
                for frame in range(9):
                    try:
                        os.remove(self.list_files[i][:-len(self.filetype)] + '_frame0' + str(frame + 1) + '.jpg')
                    except:
                        pass                
                self.text_status.set("Film " + str(i + 1) + " von " + str(len(self.list_files)) + ": sollte fertig sein...")
                root.update()
            else:
                self.text_status.set("Film " + str(i + 1) + " von " + str(len(self.list_files)) + ": kein Titel eingegeben, überspringe...")
                root.update()
        self.text_status.set("Sollte alles fertig sein")
        root.update()
    
    def create_nfo(self, filepath, timestamp, title, embarrassing):
        path_nfo = filepath[:-len(self.filetype)] + '.nfo'
        date = time.strftime("%Y-%m-%d", time.localtime(int(timestamp)))
        sorttitle = time.strftime("%Y%m%d_%H%M%S", time.localtime(int(timestamp)))
        dateadded = time.strftime("%Y-%m-%d %H:%M:%S", time.localtime(int(timestamp)))
        year = time.strftime("%Y", time.localtime(int(timestamp)))
        # write nfo file
        nfo = codecs.open(path_nfo, "w", "utf-8")
        nfo.write('<?xml version="1.0" encoding="UTF-8" standalone="yes" ?>' + '\n')
        nfo.write('<movie>' + '\n')
        nfo.write(' <title>' + date + ' ' + title + '</title>' + '\n')
        nfo.write(' <sorttitle>' + sorttitle + '</sorttitle>' + '\n')
        nfo.write(' <id>-1</id>' + '\n')
        nfo.write(' <genre>EigeneVideos</genre>' + '\n')
        nfo.write(' <set>Eigene Videos</set>' + '\n')
        nfo.write(' <year>' + year + '</year>' + '\n')
        if embarrassing == 1:
            nfo.write(' <tag>peinlich</tag>' + '\n')
        nfo.write(' <dateadded>' + dateadded + '</dateadded>' + '\n')
        nfo.write('</movie>' + '\n')
        nfo.close()
    
    def create_window_top(self):
        # define
        self.button_directory = tk.Button(text="Ordner", command=self.update_directory, takefocus = 0)
        self.label_directory = tk.Label(master=root,textvariable=self.folder_path)
        # arrange
        self.button_directory.grid(row=0, column=1)
        self.label_directory.grid(row=0, column=3, columnspan=20)
        tk.Frame(height=2, bd=1, relief=tk.SUNKEN).grid(row=1, column=1, columnspan=20, sticky="ew", pady=5)
    
    def create_window_main(self):
        # define frames
        self.imagewidth = 250
        self.canvasheight = int(self.imagewidth*9/16)
        self.var_fanart.set(4)
        self.var_poster1.set(1)
        self.var_poster2.set(7)
        self.list_canvas = []
        self.list_radiobuttons_fanart = []
        self.list_radiobuttons_poster1 = []
        self.list_radiobuttons_poster2 = []
        for i in range(9):
            row = int(10 + 10 * (i // 3))
            column = int(1 + 4 * (i % 3))
            self.list_canvas.append(tk.Canvas(root, width=self.imagewidth, height=self.canvasheight))
            self.list_canvas[i].grid(row=row, column=column, columnspan=4)
            self.list_radiobuttons_fanart.append(tk.Radiobutton(root,variable=self.var_fanart, value=i, indicatoron = 0, width = 30, text="Fanart", selectcolor='#E67E22', takefocus = 0))
            self.list_radiobuttons_fanart[i].grid(row=row+1, column=column, columnspan=4)
            self.list_radiobuttons_poster1.append(tk.Radiobutton(root,variable=self.var_poster1, value=i, indicatoron = 0, width = 30, text="Poster oben", selectcolor='#5DADE2', takefocus = 0))
            self.list_radiobuttons_poster1[i].grid(row=row+2, column=column, columnspan=4)
            self.list_radiobuttons_poster2.append(tk.Radiobutton(root,variable=self.var_poster2, value=i, indicatoron = 0, width = 30, text="Poster unten", selectcolor='#2E86C1', takefocus = 0                ))
            self.list_radiobuttons_poster2[i].grid(row=row+3, column=column, columnspan=4)
        self.load_frames(0)
        # define settings elements
        self.label_title = tk.Label(master=root,text="Titel:")
        self.entry_title = tk.Entry(master=root, width=80)
        self.entry_title.insert(0, "Bitte Ordner wählen")
        self.checkbox_embarr = tk.Checkbutton(master=root, text="peinlich?", variable=self.var_embarr, takefocus = 0)
        self.button_next = tk.Button(text="Nächstes", command=self.goto_next)
        self.button_prev = tk.Button(text="Vorheriges", command=self.goto_prev, takefocus = 0)
        self.button_work = tk.Button(text="Arbeite!", command=self.work, takefocus = 0)
        # arrange settings elements
        tk.Frame(height=2, bd=1, relief=tk.SUNKEN).grid(row=40, column=1, columnspan=20, sticky="ew", pady=5)
        self.label_title.grid(row=41, column=1)
        self.entry_title.grid(row=41, column=2, columnspan=6)
        self.checkbox_embarr.grid(row=41, column=8)
        self.button_prev.grid(row=41, column=9)
        self.button_next.grid(row=41, column=10)
        self.button_work.grid(row=41, column=11)
        tk.Frame(height=2, bd=1, relief=tk.SUNKEN).grid(row=42, column=1, columnspan=20, sticky="ew", pady=5)

    def create_window_bottom(self):
        # define
        self.label_curr_page = tk.Label(master=root,textvariable=self.text_curr_page)
        self.label_status = tk.Label(master=root,textvariable=self.text_status)
        # arrange
        self.label_curr_page.grid(row=50, column=1, columnspan=20)
        self.label_status.grid(row=51, column=1, columnspan=20)
    
    
# tkinter, do your work
root = tk.Tk()
MainWindow(root, filetype)
root.mainloop()
