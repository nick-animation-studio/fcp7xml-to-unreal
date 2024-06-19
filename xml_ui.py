from matm.Episode import Episode

from xml_helpers.reports import *
from xml_helpers.filter import *
from xml_helpers.syncsketch import *

import tkinter as tk
from tkinter import DISABLED, END, NORMAL, RIGHT, Toplevel, ttk
from tkinter import filedialog


class xmlUI:
    def __init__(self, episode=None, xml_functions=[]):
        self.current_episode = episode
        self.xml_functions = xml_functions

    def output_audio(self):
        output = audio_report(self.current_episode)
        if output is not None:
            self.show_output(output)

    def output_cgfixes(self):
        self.show_output(cgfixes_report(self.current_episode))

    def output_conform(self):
        self.show_output(conform_report(self.current_episode))

    def output_filtered_xml(self):
        self.show_output(write_filtered(self.current_episode, xml_file_string.get()))

    def output_syncsketch(self):
        self.show_output(upload(self.current_episode, ss_link.get()))

    def create_button(self, label, function):
        button = ttk.Button(frm, text=label, command=function)
        button.grid(column=len(self.xml_functions), row=2)
        button.config(state=DISABLED)
        self.xml_functions.append(button)

    def xml_to_episode(self):
        xml = filedialog.askopenfilename(
            title="Choose XML to use", filetypes=[("XMLs", "*.xml")]
        )
        xml_file_string.set(xml)
        self.current_episode = Episode(xml)
        for button in self.xml_functions:
            button.config(state=NORMAL)

    @classmethod
    def show_output(output):
        new_window = Toplevel(root)
        new_window.title("Output")

        scroll = tk.Scrollbar(new_window, orient="vertical")
        scroll.pack(side=RIGHT, fill="y")

        msg = tk.Text(new_window, yscrollcommand=scroll.set)
        msg.insert(END, output)

        scroll.config(command=msg.yview)
        msg.pack()


xml_ui = xmlUI()

root = tk.Tk()
root.resizable(True, True)
root.title("MATM -- Upload a CSV to SyncSketch")
frm = ttk.Frame(root, padding=10)
frm.grid()

xml_file_string = tk.StringVar()
xml_file_string.set("Please choose an XML file")

ss_link = tk.StringVar()
ss_link.set("If using upload, enter a syncsketch link")

xml_ui.create_button("Audio report", xml_ui.output_audio)
xml_ui.create_button("CG Fixes report", xml_ui.output_cgfixes)
xml_ui.create_button("Output filtered XML", xml_ui.output_filtered_xml)
xml_ui.create_button("Upload notes to syncsketch", xml_ui.output_syncsketch)

xml_textbox = tk.Entry(frm, textvariable=xml_file_string, width=100).grid(
    column=0, row=0, sticky="news", columnspan=len(xml_ui.xml_functions) - 1
)

ttk.Button(frm, text="Choose an xml", command=xml_ui.xml_to_episode).grid(
    column=len(xml_ui.xml_functions) - 1, row=0
)

syncsketch_textbox = tk.Entry(frm, textvariable=ss_link, width=100).grid(
    column=0, row=1, sticky="news", columnspan=len(xml_ui.xml_functions) - 1
)

root.mainloop()
