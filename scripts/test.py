# SPDX-FileCopyrightText: 2023-present Oak Ridge National Laboratory, managed by UT-Battelle
#
# SPDX-License-Identifier: BSD-3-Clause
from platform import system
from sys import platform
from tkinter import Tk, PhotoImage, LabelFrame, Entry, StringVar, Menu, DISABLED, Frame, Label, NSEW, E, VERTICAL, \
    SUNKEN, S, LEFT, BOTH, messagebox, END, BooleanVar, NORMAL, RIGHT, EW, NS, filedialog, \
    ALL, Scrollbar, SINGLE, Variable, HORIZONTAL
from tkinter.ttk import Frame, LabelFrame, Combobox, PanedWindow as ttkPanedWindow, OptionMenu

def about_dialog(self):
    messagebox.showinfo('About', message = f'This is epvf.')

root=Tk()
root.title('epvf')
pad = {'padx': 3, 'pady': 3}

height = 500
width = 1000
x = 128
y = 128

root.wm_geometry(f"{width}x{height}+{x}+{y}")
make_menu = False

if make_menu:  
    menubar = Menu(root)

    # File menu
    menu = Menu(menubar, tearoff=False)
    #menu.add_separator()
    menu.add_command(label="Quit", command=root.destroy)
    menubar.add_cascade(label="File", menu=menu)

    # Settings menu
    #menu= Menu(menubar, tearoff=False)
    #menu_settings.add_command(label="Workflow Directories", command=root._open_workflow_dir_dialog)
    #root._tk_var_keep_dialogs_open = BooleanVar(value=True)
    #menu.add_checkbutton(
    #    label="Keep Output Dialog Open", onvalue=True, offvalue=False, variable=root._tk_var_keep_dialogs_open
    #)

    #def _update_keep_dialog_open(*_):
    #    """Called whenever the checkbox is checked, updates configuration value"""
    #    root.conf.keep_dialog_open = root._tk_var_keep_dialogs_open.get()

    #root._tk_var_keep_dialogs_open.trace('w', _update_keep_dialog_open)
    #menu_settings.add_command(label="Viewers...", command=root._open_viewers_dialog)
    #menubar.add_cascade(label="Settings", menu=menu)

    menu = Menu(menubar, tearoff=False)
    #menu_help.add_command(label="EnergyPlus-Launch Documentation", command=root._open_documentation)
    menu.add_command(label="About...", command=about_dialog)
    menubar.add_cascade(label="Help", menu=menu)

    root.config(menu=menubar)

mainframe = Frame(root, padding=(3, 3, 12, 12))
mainframe.grid(column=0, row=0, sticky=NSEW)
files = LabelFrame(mainframe, text='Files')
files.grid(column=0, row=0, sticky=NSEW)
Label(files, text='IDF/epJSON').grid(column=0, row=0)
input_file = Entry(files)
input_file.grid(column=1, row=0)

def file_inputs(self):
    self.mainframe = Frame(self, padding=(3, 3, 12, 12))
    self.mainframe.grid(column=0, row=0, sticky=NSEW)
    files = LabelFrame(self.mainframe, text='Files')
    files.grid(column=0, row=0, sticky=NSEW)
    Label(files, text='IDF/epJSON').grid(column=0, row=0)
    self.input_file = Entry(files)
    self.input_file.grid(column=1, row=0)

    Label(files, text='IDF/epJSON').grid(column=0, row=1)
    self.output_file = Entry(files)
    self.output_file.grid(column=1, row=1)
    self.columnconfigure(0, weight=1)
    self.rowconfigure(0, weight=1)



root.protocol('WM_DELETE_WINDOW', root.destroy)
root.mainloop()
