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

from docopt import docopt

import photo_sort

class PhotoSortApp:
    def __init__(self, parent, input_folders):
        self.parent = parent
        self.container = Frame(parent)
        self.container.pack()

        input_text = "\n".join(input_folders)
        self.input_label = Label(self.container, text=input_text, justify=LEFT, anchor=W)
        self.input_label.pack(fill=X)

        self.year_label = Label(self.container, text="Year: *", anchor=W).pack(fill=X)
        self.year_entry = Entry(self.container)
        self.year_entry.pack()
        self.year_entry.focus()

        self.event_label = Label(self.container, text="Event: *", anchor=W).pack(fill=X)
        self.event_entry = Entry(self.container)
        self.event_entry.pack()

        self.photographer_label = Label(self.container, text="Photographer:", anchor=W).pack(fill=X)
        self.photographer_entry = Entry(self.container)
        self.photographer_entry.pack()

        self.process_button = Button(self.container)
        self.process_button["text"] = "Process"
        self.process_button.pack(side=LEFT)
        self.process_button.bind("<Button-1>", self.process_button_click)

        self.cancel_button = Button(self.container)
        self.cancel_button["text"] = "Cancel"
        self.cancel_button.pack(side=RIGHT)
        self.cancel_button.bind("<Button-1>", self.cancel_button_click)

    def cancel_button_click(self, event):
        report_event(event)
        self.parent.destroy()

    def process_button_click(self, event):
        report_event(event)
        year = self.year_entry.get()
        event = self.event_entry.get()
        photographer = self.photographer_entry.get()

        print year, event, photographer

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
    app = PhotoSortApp(root, arguments['<input>'])
    root.mainloop()

if __name__ == '__main__':
    main()

