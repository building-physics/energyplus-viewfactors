# SPDX-FileCopyrightText: 2023-present Oak Ridge National Laboratory, managed by UT-Battelle
#
# SPDX-License-Identifier: BSD-3-Clause
from platform import system
from sys import platform
from tkinter import Tk, PhotoImage, LabelFrame, Entry, StringVar, Menu, DISABLED, Frame, Label, NSEW, E, VERTICAL, \
    SUNKEN, S, LEFT, BOTH, messagebox, END, BooleanVar, NORMAL, RIGHT, EW, NS, filedialog, \
    ALL, Scrollbar, SINGLE, Variable, HORIZONTAL
from tkinter.ttk import Frame, LabelFrame, Combobox, PanedWindow as ttkPanedWindow, OptionMenu
from pathlib import Path
from .__about__ import __version__
import importlib.resources

class EnergyPlusViewFactors(Tk):

    def name(self):
        return 'EnergyPlusViewFactors'

    def __init__(self, called_from_ep_cli:bool=False, title:str='EnergyPlus View Factor Calculator',
                 min_width:int=1000, min_height:int=500):
        super().__init__(className=self.name())
        self.title(title)
        if called_from_ep_cli:
            self.option_add('*Dialog.msg.font', 'Helvetica 12')
        # Load the icon
        if system() == 'Windows':
            import ctypes
            ctypes.windll.shell32.SetCurrentProcessExplicitAppUserModelID(f"{self.name()}.{__version__}")
            with importlib.resources.path('energyplus_viewfactors.data', 'eplus.ico') as icon_path:
                if icon_path.exists():
                    self.iconbitmap(icon_path)
                else:
                    print(f"Could not set icon, expecting to find it at {icon_path}")
        else:
            icon_file_name = 'eplus256.png'
            if system() == 'Darwin':
                icon_file_name = 'ep.icns'
            with importlib.resources.path('energyplus_viewfactors.data', icon_file_name) as icon_path:
                if icon_path.exists():
                    img = PhotoImage(file=str(icon_path))
                    self.iconphoto(False, img)
                else:
                    print(f"Could not set icon, expecting to find it at {icon_path}")
        self.pad = {'padx': 3, 'pady': 3}

        self.gui()

        # set the minimum size and redraw the app
        #self.minsize(min_width, min_height)
        self.update()

        # one time update of the status bar
        #self._update_status_bar("Program Initialized")

        # potentially show a welcome screen if we are on a new version
        #self._open_welcome()

        # Bind keys and focus events
        self.bind('<Key>', self.handle_keypress)
        self.bind("<FocusIn>", self.handle_focus_in)

    def handle_keypress(self, event) -> None:
        pass

    def handle_focus_in(self, _event) -> None:
        pass

    def gui(self):
        self.top_menu()
        self.frame = Frame(self, padding=(3, 3, 12, 12))
        self.frame.grid(column=0, row=0, sticky=NSEW)
        self.file_inputs()

        height = 500
        width = 1000
        x = 128
        y = 128

        self.wm_geometry(f"{width}x{height}+{x}+{y}")

    def top_menu(self):
        menubar = Menu(self)

        # File menu
        menu = Menu(menubar, tearoff=False)
        #menu.add_separator()
        menu.add_command(label="Quit", command=self.window_close)
        menubar.add_cascade(label="File", menu=menu)

        # Settings menu
        #menu= Menu(menubar, tearoff=False)
        #menu_settings.add_command(label="Workflow Directories", command=self._open_workflow_dir_dialog)
        #self._tk_var_keep_dialogs_open = BooleanVar(value=True)
        #menu.add_checkbutton(
        #    label="Keep Output Dialog Open", onvalue=True, offvalue=False, variable=self._tk_var_keep_dialogs_open
        #)

        #def _update_keep_dialog_open(*_):
        #    """Called whenever the checkbox is checked, updates configuration value"""
        #    self.conf.keep_dialog_open = self._tk_var_keep_dialogs_open.get()

        #self._tk_var_keep_dialogs_open.trace('w', _update_keep_dialog_open)
        #menu_settings.add_command(label="Viewers...", command=self._open_viewers_dialog)
        #menubar.add_cascade(label="Settings", menu=menu)

        menu = Menu(menubar, tearoff=False)
        #menu_help.add_command(label="EnergyPlus-Launch Documentation", command=self._open_documentation)
        menu.add_command(label="About...", command=self.about_dialog)
        menubar.add_cascade(label="Help", menu=menu)

        self.config(menu=menubar)

    def file_inputs(self):
        files = LabelFrame(self.frame, text='Files')
        files.grid(column=0, row=0, sticky=NSEW)

        Label(files, text='IDF/epJSON').grid(column=0, row=0, sticky=EW)
        self.input_file = Entry(files)
        self.input_file.grid(column=1, row=0, sticky=EW)

        #Label(files, text='Output').grid(column=0, row=1)
        #self.output_file = Entry(files)
        #self.output_file.grid(column=1, row=1)
        #self.columnconfigure(0, weight=1)
        #self.rowconfigure(0, weight=1)

    def about_dialog(self):
        messagebox.showinfo('About', message = f'This is the {self.title()}, version {__version__}.')

    def run(self):
        self.protocol('WM_DELETE_WINDOW', self.window_close)
        self.mainloop()

    def window_close(self, *_):
        self.destroy()