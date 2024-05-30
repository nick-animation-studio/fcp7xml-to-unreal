from email.mime import audio
import tkinter as tk
from tkinter import END, RIGHT, Toplevel, ttk
from tkinter import filedialog

from xml_helpers.ingest import *
from xml_helpers.reports import *

CURRENT_EPISODE = None


def xml_to_episode():
    xml = filedialog.askopenfilename(
        title="Choose XML to use", filetypes=[("XMLs", "*.xml")]
    )
    xml_file_string.set(xml)
    global CURRENT_EPISODE
    CURRENT_EPISODE = ingest(xml)


def show_output(output):
    new_window = Toplevel(root)
    new_window.title("Output")

    scroll = tk.Scrollbar(new_window, orient="vertical")
    scroll.pack(side=RIGHT, fill="y")

    msg = tk.Text(new_window, yscrollcommand=scroll.set)
    msg.insert(END, output)

    scroll.config(command=msg.yview)
    msg.pack()


def output_audio():
    output = audio_report(CURRENT_EPISODE)
    if output is not None:
        show_output(output)


def output_cgfixes():
    show_output(cgfixes_report(CURRENT_EPISODE))


def output_conform():
    show_output(conform_report(CURRENT_EPISODE))


root = tk.Tk()
root.geometry("600x150")
root.resizable(True, True)
root.title("MATM -- Upload a CSV to SyncSketch")
frm = ttk.Frame(root, padding=10)
frm.grid()

xml_file_string = tk.StringVar()
xml_file_string.set("Please choose an XML file")

ss_textbox = tk.Entry(frm, textvariable=xml_file_string, width=100).grid(
    column=0, row=0, sticky="news", columnspan=3
)
ttk.Button(frm, text="Choose an xml", command=xml_to_episode).grid(column=1, row=1)

ttk.Button(frm, text="Audio report", command=output_audio).grid(column=0, row=2)
ttk.Button(frm, text="CG Fixes report", command=output_cgfixes).grid(column=1, row=2)
ttk.Button(frm, text="Conform report", command=output_conform).grid(column=2, row=2)
root.mainloop()
