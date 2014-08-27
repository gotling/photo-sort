#!/usr/bin/env python
# -*- coding: utf-8 -*-

"""Photo Sort GUI

Usage:
    photo_sort_gui.py <input> ...
"""

__author__ = "Marcus Götling"
__license__ = "MIT"
__email__ = "marcus@gotling.se"

import sys
from Tkinter import *
import tkFileDialog

from docopt import docopt

import photo_sort

class PhotoSortApp:
    def __init__(self, parent, input_folders):
        self.photoSort = photo_sort.PhotoSort(False, False)

        self.app_parent = parent
        self.input_folders = input_folders
        self.container = Frame(parent)
        self.container.grid(padx=5, pady=5)
        #self.container.pack()

        input_text = "\n".join(input_folders)
        self.input_label = Label(self.container, text=input_text, justify=LEFT, anchor=W)
        self.input_label.grid(columnspan=2, sticky=W)

        Label(self.container, text="Year: *", anchor=W).grid(row=1, sticky=W)
        self.year_entry = Entry(self.container)
        self.year_entry.grid(row=1, column=1)
        self.year_entry.focus()

        Label(self.container, text="Event: *", anchor=W).grid(row=2, sticky=W)
        self.event_entry = Entry(self.container)
        self.event_entry.grid(row=2, column=1)

        Label(self.container, text="Photographer:", anchor=W).grid(row=3, sticky=W)
        self.photographer_entry = Entry(self.container)
        self.photographer_entry.grid(row=3, column=1)

        self.process_button = Button(self.container)
        self.process_button["text"] = "Process"
        self.process_button.grid(row=4, sticky=W)
        self.process_button.bind("<Button-1>", self.process_button_click)

        self.cancel_button = Button(self.container)
        self.cancel_button["text"] = "Cancel"
        self.cancel_button.grid(row=4, column=1, sticky=E)
        self.cancel_button.bind("<Button-1>", self.cancel_button_click)

        self.status_string = StringVar()
        self.status_string.set("Fill in fields and press Process to start")
        self.status_label = Label(self.container, textvariable=self.status_string, justify=LEFT, anchor=W)
        self.status_label.grid(row=5, columnspan=2, sticky=W)

    def cancel_button_click(self, event):
        report_event(event)
        self.app_parent.destroy()

    def process_button_click(self, event):
        report_event(event)
        year = self.year_entry.get().strip()
        event = self.event_entry.get().strip()
        photographer = self.photographer_entry.get().strip()
        
        if check_fields(year, event, photographer):
            self.status_string.set("Choose output folder.")
            output = tkFileDialog.askdirectory(title="Choose output folder", initialdir=self.input_folders[0], mustexist=True)
            if output != "":
                self.status_string.set("Processing folders. Please wait...")
                self.photoSort.process(self.input_folders, output, year, event, photographer)
                self.status_string.set("Done!")
        else:
            self.status_string.set("Please fill in required fields correctly.")

def check_fields(year, event, photographer):
    valid = True
    if len(year) != 4:
        valid = False

    if len(event) == 0:
        valid = False

    return valid

def report_event(event):
    """Print a description of an event, based on its attributes.
    """
    event_name = {"2": "KeyPress", "4": "ButtonPress"}
    print "Time:", str(event.time)
    print "EventType=" + str(event.type), \
        event_name[str(event.type)],\
        "EventWidgetId=" + str(event.widget), \
        "EventKeySymbol=" + str(event.keysym)

def main():
    arguments = docopt(__doc__, version='Photo Sort GUI 1.0.0')

    root = Tk()
    root.wm_title("Photo Sort")
    root.resizable(width=FALSE, height=FALSE)
    app = PhotoSortApp(root, arguments['<input>'])
    root.mainloop()

if __name__ == '__main__':
    main()
