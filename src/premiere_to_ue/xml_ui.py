import tkinter as tk
from tkinter import DISABLED, END, NORMAL, RIGHT, Toplevel, filedialog, messagebox, ttk

from premiere_to_ue import __version__
from premiere_to_ue.models.Episode import Episode
from premiere_to_ue.xml_helpers.reports import (
    audio_report,
    cgfixes_report,
    conform_report,
)


class xmlUI:
    def __init__(
        self,
        root=None,
        frm=None,
        xml_file_string="",
        episode=None,
        xml_functions=None,
    ):
        if xml_functions is None:
            xml_functions = []
        self.root = root
        self.frm = frm
        self.xml_file_string = xml_file_string
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
        self.current_episode.write_filtered()

    def create_button(self, label, function):
        button = ttk.Button(self.frm, text=label, command=function)
        button.grid(column=len(self.xml_functions), row=2)
        button.config(state=DISABLED)
        self.xml_functions.append(button)

    def xml_to_episode(self):
        xml_path = filedialog.askopenfilename(
            title="Choose XML to use", filetypes=[("XMLs", "*.xml")]
        )
        if not xml_path:
            messagebox.showinfo("Info", "No XML file selected.")
            return

        # try:
        self.xml_file_string.set(xml_path)
        self.current_episode = Episode(xml_path)
        for button in self.xml_functions:
            button.config(state=NORMAL)

        report_output = "Ingest logs:\n\n"
        report_output += self.current_episode.ingest_log
        report_output += "\n\n"

        report_output += "Conform Report:\n\n"
        report_output += conform_report(self.current_episode)
        report_output += "\n\n"

        report_output += "CG Fixes Report:\n\n"
        report_output += cgfixes_report(self.current_episode)
        report_output += "\n\n"

        self.show_output(report_output)
        # except Exception as e:
        #    messagebox.showerror("Error", f"Could not process XML file:\n{e}")

    def show_output(self, output):
        if len(output) == 0:
            output = "No errors found!"
        new_window = Toplevel(self.root)
        new_window.title("Output")

        scroll = tk.Scrollbar(new_window, orient="vertical")
        scroll.pack(side=RIGHT, fill="y")

        msg = tk.Text(new_window, yscrollcommand=scroll.set)
        msg.insert(END, output)

        scroll.config(command=msg.yview)
        msg.pack(side="top", fill="both", expand="True")


def main():
    root = tk.Tk()
    root.resizable(True, True)
    root.title(f"Premiere to UE XML utility v{__version__}")
    frm = ttk.Frame(root, padding=10)
    frm.grid()

    xml_file_string = tk.StringVar()
    xml_file_string.set("Please choose an XML file")

    xml_ui = xmlUI(root=root, frm=frm, xml_file_string=xml_file_string)

    xml_ui.create_button("Audio report", xml_ui.output_audio)
    # xml_ui.create_button("CG Fixes report", xml_ui.output_cgfixes)
    # xml_ui.create_button("Conform report", xml_ui.output_conform)
    xml_ui.create_button("Output filtered XML", xml_ui.output_filtered_xml)

    tk.Entry(frm, textvariable=xml_file_string, width=100).grid(
        column=0, row=0, sticky="news", columnspan=len(xml_ui.xml_functions)
    )

    ttk.Button(frm, text="Choose an xml", command=xml_ui.xml_to_episode).grid(
        column=len(xml_ui.xml_functions), row=0
    )

    root.mainloop()


if __name__ == "__main__":
    main()
