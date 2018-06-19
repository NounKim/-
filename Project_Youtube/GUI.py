import configparser
import os
import tkinter as tk
import tkinter.filedialog
import youtube_dl
import threading
import time
import webbrowser

import spam

import smtplib
from email.mime.text import MIMEText
from email.mime.multipart import MIMEMultipart
from email.mime.base import MIMEBase
from email import encoders



# Separate StatusBar class for code clarity
class StatusBar(tk.Frame):
    def __init__(self, master):
        tk.Frame.__init__(self, master)
        self.label = tk.Label(self, bd=1, relief="sunken", anchor="w")
        self.label.pack(fill="x")

    def set(self, sFormat, *args):
        self.label.config(text=sFormat % args)
        self.label.update_idletasks()

    def clear(self):
        self.label.config(text="")
        self.label.update_idletasks()

# Main GUI class
class GUI:
    # Constructor
    def __init__(self, master):
        self.master = master
        # Create config.ini if it doesn't exist
        self.createDefaultConfig()

        # Setup for the program to use config.ini variables
        self.originalCwd = os.getcwd()
        config = configparser.RawConfigParser()
        config.read(self.originalCwd + "\config.ini")

        # Variables
        self.optionAudio = tk.BooleanVar(master, config["Options"]["audioonly"])
        self.optionHTTP = tk.BooleanVar(master, config["Options"]["usehttp"])
        self.optionBypass = tk.BooleanVar(master, config["Options"]["bypassgeo"])

        self.defaultOutput = tk.StringVar(master, config["Options"]["nameformat"])
        self.defaultPath = tk.StringVar(master, config["Options"]["path"])
        self.defaultFile = tk.StringVar()

        self.defaultUsername = tk.StringVar(master, config["Options"]["username"])
        self.defaultPassword = tk.StringVar(master, config["Options"]["password"])
        self.defaultRecipient = tk.StringVar(master, config["Options"]["recipient"])

        self.ytdlOptions = {"quiet": False}

        # Setting up the window
        # Title
        master.title("유튜브 다운로더")

        # Disable resizing
        master.resizable(width=False, height=False)

        # Icon
        if os.path.isfile("icon_tube.ico"):
            master.iconbitmap(default="icon_tube.ico")


        # Menu Bar
        menuBar = tk.Menu(master, bg="grey")
        menuBar.add_command(label="간편", command=self.basicPress)
        menuBar.add_command(label="상세설정", command=self.advancedPress)
        menuBar.add_command(label="깃허브 연결", command=self.aboutPress)
        master.config(menu=menuBar)

        # Main Frame
        self.mainFrame = tk.Frame(master)
        self.mainFrame.grid_columnconfigure(1, weight=1)
        self.mainFrame.pack(fill="both", expand=True)

        # Layout
        self.basicPress()

        # Status Bar
        self.statusBar = StatusBar(master)
        self.statusBar.set("대기 중...")
        self.statusBar.pack(side="bottom", fill="x")

    # Basic menu button
    def basicPress(self):
        self.mainFrame.destroy()

        # Set Window Size
        self.master.geometry("500x200")

        # Main Frame
        self.mainFrame = tk.Frame(self.master)
        self.mainFrame.grid_columnconfigure(1, weight=1)
        self.mainFrame.pack(fill="both", expand=True)

        # Entries
        linkEntryLabel = tk.Label(self.mainFrame, text="YouTube URL")
        self.linkEntry = tk.Entry(self.mainFrame)
        saveEntryLabel = tk.Label(self.mainFrame, text="저장할 폴더")
        saveEntry = tk.Entry(self.mainFrame, textvariable=self.defaultPath)

        linkEntryLabel.grid(row=0, column=0, padx=5, pady=(5, 0), sticky="w")
        self.linkEntry.grid(row=1, column=0, columnspan=3, padx=5, pady=0, sticky="we")
        saveEntryLabel.grid(row=2, column=0, padx=5, pady=(5, 0), sticky="w")
        saveEntry.grid(row=3, column=0, columnspan=2, padx=5, pady=0, sticky="we")

        # Buttons
        chooseCwdButton = tk.Button(self.mainFrame, text="검색...", command=self.browsePress)
        downloadButton = tk.Button(self.mainFrame, text="다운로드", command=self.downloadPress)

        chooseCwdButton.grid(row=3, column=2, padx=5, pady=0, sticky="we")
        downloadButton.grid(row=12, column=2, padx=5, pady=(5, 0), sticky="e")


        # Options
        audioCheck = tk.Checkbutton(self.mainFrame, text="소리만 다운로드", variable=self.optionAudio)
        audioCheck.grid(row=12, column=0, padx=5, pady=(5, 0), sticky="w")

    # Advanced menu button
    def advancedPress(self):
        # Set window size
        self.master.geometry("500x500")

        # Entires
        outputLabel = tk.Label(self.mainFrame, text="서식")
        outputEntry = tk.Entry(self.mainFrame, textvariable=self.defaultOutput)
        usernameLabel = tk.Label(self.mainFrame, text="Username/Email")
        usernameEntry = tk.Entry(self.mainFrame, textvariable=self.defaultUsername)
        passwordLabel = tk.Label(self.mainFrame, text="Password")
        passwordEntry = tk.Entry(self.mainFrame, textvariable=self.defaultPassword, show="*")
        sendnameLabel = tk.Label(self.mainFrame, text="Recipient/Email")
        sendnameEntry = tk.Entry(self.mainFrame, textvariable=self.defaultRecipient)
        choosefileLabel = tk.Label(self.mainFrame, text="파일 이름")
        choosefileEntry = tk.Entry(self.mainFrame, textvariable=self.defaultFile)
        choosefileButton = tk.Button(self.mainFrame, text = '검색..?', command=self.browseFile)
        sendButton = tk.Button(self.mainFrame, text="메일로 보내기", command=self.sendPress)


        outputLabel.grid(row=4, column=0, padx=5, pady=(5, 0), sticky="w")
        outputEntry.grid(row=5, column=0, columnspan=3, padx=5, pady=0, sticky="we")
        usernameLabel.grid(row=6, column=0, padx=5, pady=(5, 0), sticky="w")
        usernameEntry.grid(row=7, column=0, columnspan=3, padx=5, pady=0, sticky="we")
        passwordLabel.grid(row=8, column=0, padx=5, pady=(5, 0), sticky="w")
        passwordEntry.grid(row=9, column=0, columnspan=3, padx=5, pady=0, sticky="we")
        sendnameLabel.grid(row=10, column=0, padx=5, pady=(5, 0), sticky="w")
        sendnameEntry.grid(row=11, column=0, columnspan=3, padx=5, pady=0, sticky="we")
        choosefileLabel.grid(row=14, column=0, padx=5, pady=(5, 0), sticky="w")
        choosefileEntry.grid(row=15, column=0, columnspan=2, padx=5, pady=0, sticky="we")
        choosefileButton.grid(row=15, column=2, padx=5, pady=0, sticky="we")
        sendButton.grid(row=16, column=2, padx=5, pady=(5, 0), sticky="e")


        # Options
        httpCheck = tk.Checkbutton(self.mainFrame, text="HTTP 사용", variable=self.optionHTTP)
        httpCheck.grid(row=12, column=1, padx=5, pady=(5, 0), sticky="w")
        bypassCheck = tk.Checkbutton(self.mainFrame, text="지리적 제한 무시", variable=self.optionBypass)
        bypassCheck.grid(row=13, column=0, columnspan=3, padx=5, pady=(5, 0), sticky="w")

    # About menu button
    def aboutPress(self):
        webbrowser.open(r"https://github.com/NounKim/-")

    # Browse button functionality. Choose directory.
    def browsePress(self):
        path = tk.filedialog.askdirectory()
        if path != "":
            self.defaultPath.set(path)

    # Browse button functionality. Choose file.
    def browseFile(self):
        file = tk.filedialog.askopenfilename()
        if file != "":
            self.defaultFile.set(file)

    # Download button functionality. Download video with options.
    def downloadPress(self):
        t = threading.Thread(target=self.downloadAction)
        t.start()

    # Send button functionality. Downloaded video to recipient
    def sendPress(self):
        email_user = self.defaultUsername.get()
        email_password = self.defaultPassword.get()
        email_send = self.defaultRecipient.get()

        subject = 'subject'

        msg = MIMEMultipart()
        msg['From'] = email_user
        msg['To'] = email_send
        msg['Subject'] = subject

        filename = self.defaultFile.get()
        attachment = open(filename, 'rb')

        part = MIMEBase('application', 'octet-stream')
        part.set_payload((attachment).read())
        encoders.encode_base64(part)
        part.add_header('Content-Disposition', "attachment; filename= " + filename)

        msg.attach(part)
        text = msg.as_string()

        ####
        if 'gmail' in email_user:
            server = smtplib.SMTP('smtp.gmail.com', 587)

        if 'naver' in email_user:
            server = smtplib.SMTP('smtp.naver.com', 587)

        server.starttls()
        server.login(email_user, email_password)

        server.sendmail(email_user, email_send, text)
        server.quit()
        pass

    # Only to be called from downloadPress()
    def downloadAction(self):
        # Updates status bar -> updates config file -> updates ytdlOptions -> downloads video/audio -> update status bar
        self.statusBar.set("config.ini 업데이트 중...")
        self.updateAllConfigFile()
        self.updateOptionDictionary()
        self.statusBar.set("다운로드 중...")
        with youtube_dl.YoutubeDL(self.ytdlOptions) as ytdler:
            try:
                ytdler.download([self.linkEntry.get()])
                self.statusBar.set("완료")
            except youtube_dl.utils.YoutubeDLError:
                self.statusBar.set("다운로드 실패")
        time.sleep(10)
        self.statusBar.set("대기 중...")

    # Update all settings in config.ini
    def updateAllConfigFile(self):
        self.updateConfigFile("Options", "path", self.defaultPath.get())
        self.updateConfigFile("Options", "nameformat", self.defaultOutput.get())
        self.updateConfigFile("Options", "audioonly", str(self.optionAudio.get()))
        self.updateConfigFile("Options", "usehttp", str(self.optionHTTP.get()))
        self.updateConfigFile("Options", "bypassgeo", str(self.optionBypass.get()))
        self.updateConfigFile("Options", "username", str(self.defaultUsername.get()))
        self.updateConfigFile("Options", "recipient", str(self.defaultRecipient.get()))

    # Updates ytdlOptions.
    def updateOptionDictionary(self):
        config = configparser.RawConfigParser()
        config.read(self.originalCwd + "\config.ini")
        # path and filename option
        self.ytdlOptions["outtmpl"] = config["Options"]["path"] + "\\" + config["Options"]["nameformat"]

        # Audio Only
        if self.optionAudio.get():  # If 'Audio Only' is Checked
            self.ytdlOptions["format"] = "bestaudio[ext=m4a]/best"
            self.ytdlOptions["postprocessors"] = [{"key": "FFmpegExtractAudio",
                                                  "preferredcodec": "mp3",
                                                  "preferredquality": "192"}]
        else:  # If 'Audio Only' is Unchecked
            if "postprocessors" in self.ytdlOptions.keys():
                del self.ytdlOptions["postprocessors"]
            self.ytdlOptions["format"] = "bestvideo[ext=mp4]+bestaudio[ext=m4a]/best"

        # Use HTTP
        self.ytdlOptions["prefer_insecure"] = self.optionHTTP.get()

        # Bypass Geo Restiction (experimental)
        self.ytdlOptions["geo_bypass"] = self.optionBypass.get()

        # Username + Password
        if not self.defaultUsername.get() == "":  # If a username is present
            if not self.defaultPassword.get() == "":  # If a password is present
                self.ytdlOptions["username"] = self.defaultUsername.get()
                self.ytdlOptions["password"] = self.defaultPassword.get()

    # Create default config file if it doesn't exist
    def createDefaultConfig(self):
        if os.path.isfile(os.getcwd() + "\config.ini"):
            pass
        else:
            config = configparser.RawConfigParser()
            config["Options"] = {"path": os.getcwd(),
                                 "nameformat": "%(title)s.%(ext)s",
                                 "audioonly": False,
                                 "usehttp": False,
                                 "bypassgeo": False,
                                 "username": "",
                                 "password": "",
                                 "recipient": ""
                                 }

            with open("config.ini", "w") as configfile:
                config.write(configfile)

    # Update one setting in config.ini
    # Only used in updateConfigFile()
    def updateConfigFile(self, heading, variable, result):
        # heading = the heading in the configuration file e.g. [Options]
        # variable = the variable under the heading e.g. path
        # result = what is stored in the variable e.g. C:\Hello_World\Example
        config = configparser.RawConfigParser()
        config.read(self.originalCwd + "\config.ini")
        config[heading][variable] = result

        with open(self.originalCwd + "\config.ini", "w") as configfile:
            config.write(configfile)

if __name__ == '__main__':
    root = tk.Tk()
    window = GUI(root)
    root.mainloop()

