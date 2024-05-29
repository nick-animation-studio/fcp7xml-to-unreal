import tkinter as tk
from tkinter import ttk
from tkinter import filedialog

from xml_helpers.ingest import *


def xml_to_episode():
    xml = filedialog.askopenfilename(
        title="Choose XML to use", filetypes=[("XMLs", "*.xml")]
    )
    episode = ingest(xml)
    for shot in episode.shots:
        print(shot.notes)


root = tk.Tk()
root.geometry("600x150")
root.resizable(True, True)
root.title("MATM -- Upload a CSV to SyncSketch")
frm = ttk.Frame(root, padding=10)
frm.grid()

xml_file_string = tk.StringVar()
xml_file_string.set("Please choose an XML file")

ss_textbox = tk.Entry(frm, textvariable=xml_file_string, width=100).grid(
    column=0, row=0, sticky="news"
)
ttk.Button(frm, text="Choose an xml", command=xml_to_episode).grid(column=0, row=1)


root.mainloop()
