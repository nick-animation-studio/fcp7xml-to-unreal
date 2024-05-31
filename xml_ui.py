from email.mime import audio
import tkinter as tk
from tkinter import DISABLED, END, NORMAL, RIGHT, Toplevel, ttk
from tkinter import filedialog
from xml.etree.ElementTree import XML

from xml_helpers.ingest import *
from xml_helpers.reports import *
from xml_helpers.filter import *

CURRENT_EPISODE = None
XML_FUNCTIONS = []


def create_button(label, function):
    global XML_FUNCTIONS
    button = ttk.Button(frm, text=label, command=function)
    button.grid(column=len(XML_FUNCTIONS), row=1)
    button.config(state=DISABLED)
    XML_FUNCTIONS.append(button)


def xml_to_episode():
    xml = filedialog.askopenfilename(
        title="Choose XML to use", filetypes=[("XMLs", "*.xml")]
    )
    xml_file_string.set(xml)
    global CURRENT_EPISODE
    CURRENT_EPISODE = ingest(xml)
    for button in XML_FUNCTIONS:
        button.config(state=NORMAL)


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


def output_filtered_xml():
    show_output(write_filtered(CURRENT_EPISODE, xml_file_string.get()))


root = tk.Tk()
root.resizable(True, True)
root.title("MATM -- Upload a CSV to SyncSketch")
frm = ttk.Frame(root, padding=10)
frm.grid()

xml_file_string = tk.StringVar()
xml_file_string.set("Please choose an XML file")


create_button("Audio report", output_audio)
create_button("CG Fixes report", output_cgfixes)
create_button("Conform report", output_conform)
create_button("Output filtered XML", output_filtered_xml)

ss_textbox = tk.Entry(frm, textvariable=xml_file_string, width=100).grid(
    column=0, row=0, sticky="news", columnspan=len(XML_FUNCTIONS) - 1
)

ttk.Button(frm, text="Choose an xml", command=xml_to_episode).grid(
    column=len(XML_FUNCTIONS) - 1, row=0
)

root.mainloop()
