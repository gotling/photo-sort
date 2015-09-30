#!/usr/bin/env python
# -*- coding: utf-8 -*-

"""Photo Sort GUI

Usage:
    photo_sort_gui.py <input> ...
"""

import os
from tkinter import *
import tkinter as tk
import tkinter.filedialog
from tkinter.messagebox import askyesno

from docopt import docopt
import photo_sort
from enums import Mode

__author__ = "Marcus Götling"
__license__ = "MIT"
__email__ = "marcus@gotling.se"


class PhotoSortApp:
    def __init__(self, parent, input_folders):
        self.app_parent = parent
        self.input_folders = input_folders
        self.container = Frame(parent)
        self.container.grid(padx=10, pady=10)

        Label(self.container, text="Folders:", anchor=W).grid(row=0, sticky=W)
        input_text = "\n".join(input_folders)
        self.input_label = Label(self.container, text=input_text, justify=LEFT, anchor=W)
        self.input_label.grid(row=0, column=1, columnspan=3, sticky=W)

        Label(self.container, text="Name:", anchor=W).grid(row=1, sticky=W)
        self.event_entry = Entry(self.container)
        self.event_entry.grid(row=1, column=1, sticky=W)
        self.event_entry.focus()

        Label(self.container, text="Year:", anchor=W).grid(row=1, column=3, sticky=W)
        self.year_entry = Entry(self.container)
        self.year_entry.grid(row=1, column=4, sticky=W)

        Label(self.container, text="Sub Name:", anchor=W).grid(row=2, sticky=W)
        self.sub_event_entry = Entry(self.container)
        self.sub_event_entry.grid(row=2, column=1, sticky=W)

        Label(self.container, text="Photographer:", anchor=W).grid(row=2, column=3, sticky=W)
        self.photographer_entry = Entry(self.container)
        self.photographer_entry.grid(row=2, column=4, sticky=W)

        self.mode = IntVar()
        self.mode.set(Mode.replace.value)
        Radiobutton(self.container, text='Rename', variable=self.mode, value=Mode.replace.value).grid(row=3, sticky=W)
        Radiobutton(self.container, text='Copy', variable=self.mode, value=Mode.copy.value).grid(row=3, column=1, sticky=W)
        Radiobutton(self.container, text='Move', variable=self.mode, value=Mode.move.value).grid(row=3, column=2, columnspan=3, sticky=W)

        self.encode = BooleanVar()
        self.encode.set(True)
        Checkbutton(self.container, text="Encode videos", variable=self.encode).grid(row=4, sticky=W)

        self.decomb = BooleanVar()
        self.decomb.set(False)
        Checkbutton(self.container, text="Decomb to remove horizontal lines", variable=self.decomb).grid(row=4, column=2, columnspan=2, sticky=W)

        self.process_button = Button(self.container)
        self.process_button["text"] = "Process"
        self.process_button.grid(row=5, sticky=W)
        self.process_button.bind("<Button-1>", self.process_button_click)

        bottom_panel = Frame(self.container, borderwidth=1, relief="sunken")
        bottom_panel.grid(row=8, columnspan=5)
        self.console_string = "Fill in fields and press Process to start\n"

        scrollbar = tk.Scrollbar(orient="vertical", borderwidth=1)
        # N.B. height is irrelevant; it will be as high as it needs to be
        self.console_text = tk.Text(background="white", width=80, height=8, borderwidth=0, yscrollcommand=scrollbar.set)
        scrollbar.config(command=self.console_text.yview)

        self.console_text.grid(in_=bottom_panel, row=0, column=0, columnspan=3, sticky="nsew")
        scrollbar.grid(in_=bottom_panel, row=0, column=3, sticky="ns")
        bottom_panel.grid_rowconfigure(1, weight=1)
        bottom_panel.grid_columnconfigure(0, weight=1)

        self.console_text.insert(END, self.console_string)

    def cancel_button_click(self, event):
        report_event(event)
        self.app_parent.destroy()

    def process_button_click(self, event):
        report_event(event)
        self.prepare()

    def prepare(self):
        year = self.year_entry.get().strip()
        event = self.event_entry.get().strip()
        sub_event = self.sub_event_entry.get().strip()
        photographer = self.photographer_entry.get().strip()

        if Mode(self.mode.get()) == Mode.replace:
            mode = Mode.move
            output = None
        else:
            self.log("Choose output folder.")
            dialog_dir = os.path.abspath(os.path.join(self.input_folders[0], os.pardir))
            output = tkinter.filedialog.askdirectory(title="Choose output folder", initialdir=dialog_dir, mustexist=True)
            if output == "":
                return
            mode = self.mode.get()

        self.log("Processing folders. Please wait...")
        self.photoSort = photo_sort.PhotoSort(self.input_folders, output, year, event, sub_event, photographer,
                                              encode=False, dry_run=False, decomb=self.decomb)
        self.photoSort.set_mode(mode)
        self.photoSort.set_encode_videos(self.encode.get())

        self.confirm_rename_dialog()

    def confirm_rename_dialog(self):
        if askyesno('Verify changes below', self.photoSort.get_preview() + "\n\nContinue?"):
            self.rename()
        else:
            self.log("Canceled")
            return

    def rename(self):
        self.photoSort.process()
        self.log("Done!")

    def log(self, string):
        self.console_text.insert(END, string + "\n")
        self.console_text.see(END)


def report_event(event):
    """Print a description of an event, based on its attributes.
    """
    event_name = {"2": "KeyPress", "4": "ButtonPress"}
    print("Time:", str(event.time))
    print("EventType=" + str(event.type),
          event_name[str(event.type)],
          "EventWidgetId=" + str(event.widget),
          "EventKeySymbol=" + str(event.keysym))


def main():
    arguments = docopt(__doc__, version=photo_sort.version)

    root = Tk()
    root.wm_title("Photo Sort")
    root.resizable(width=FALSE, height=FALSE)
    PhotoSortApp(root, arguments['<input>'])
    root.mainloop()

if __name__ == '__main__':
    main()

