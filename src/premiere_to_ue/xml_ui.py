import tkinter as tk
from tkinter import DISABLED, END, NORMAL, RIGHT, Toplevel, filedialog, messagebox, ttk

from premiere_to_ue import __version__
from premiere_to_ue.models.Episode import Episode
from premiere_to_ue.xml_helpers.reports import (
    audio_report,
    cgfixes_report,
    conform_report,
)
from premiere_to_ue.xml_helpers.syncsketch import get_name, upload


class xmlUI:
    def __init__(
        self,
        root=None,
        ss_link=None,
        frm=None,
        xml_file_string="",
        episode=None,
        xml_functions=[],
    ):
        self.root = root
        self.ss_link = ss_link
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
        self.show_output(self.current_episode.write_filtered())

    def confirm_upload(self):
        new_window = Toplevel(self.root)
        new_window.resizable(True, True)
        new_window.title("Confirm Upload")

        xml_name = self.current_episode.file.rsplit("/", 1)[1]
        syncsketch_name = get_name(self.ss_link.get())

        frm = ttk.Frame(new_window, padding=10)
        frm.grid()

        ttk.Label(frm, text=f"Upload notes from {xml_name} to {syncsketch_name}?").grid(
            column=0, row=0
        )
        ttk.Button(frm, text="Confirm", command=self.output_syncsketch).grid(
            column=0, row=1
        )

    def output_syncsketch(self):
        self.show_output(upload(self.current_episode, self.ss_link.get()))

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

        try:
            self.xml_file_string.set(xml_path)
            self.current_episode = Episode(xml_path)
            for button in self.xml_functions:
                button.config(state=NORMAL)

            report_output = (
                "Aggregate Reports - please scroll down and check all 3!\n\n"
            )

            report_output += "Ingest logs:\n\n"
            report_output += self.current_episode.ingest_log
            report_output += "\n\n"

            report_output += "Conform Report:\n\n"
            report_output += conform_report(self.current_episode)
            report_output += "\n\n"

            report_output += "CG Fixes Report:\n\n"
            report_output += cgfixes_report(self.current_episode)
            report_output += "\n\n"

            self.show_output(report_output)
        except Exception as e:
            messagebox.showerror("Error", f"Could not process XML file:\n{e}")

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

    ss_link = tk.StringVar()
    ss_link.set("If using upload, enter a syncsketch link")

    xml_ui = xmlUI(root=root, frm=frm, ss_link=ss_link, xml_file_string=xml_file_string)

    xml_ui.create_button("Audio report", xml_ui.output_audio)
    # xml_ui.create_button("CG Fixes report", xml_ui.output_cgfixes)
    # xml_ui.create_button("Conform report", xml_ui.output_conform)
    xml_ui.create_button("Output filtered XML", xml_ui.output_filtered_xml)
    xml_ui.create_button("Upload notes to syncsketch", xml_ui.confirm_upload)

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


if __name__ == "__main__":
    main()
