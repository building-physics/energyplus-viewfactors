# SPDX-FileCopyrightText: 2023-present Oak Ridge National Laboratory, managed by UT-Battelle
#
# SPDX-License-Identifier: BSD-3-Clause
from platform import system
from sys import platform
from tkinter import Tk, PhotoImage, Entry, StringVar, Menu, DISABLED, Label, NSEW, E, VERTICAL, \
    SUNKEN, S, LEFT, BOTH, messagebox, END, BooleanVar, NORMAL, RIGHT, EW, NS, filedialog, \
    ALL, Scrollbar, SINGLE, Variable, HORIZONTAL, Listbox, ACTIVE
from tkinter.ttk import Frame, LabelFrame, Checkbutton, Combobox, PanedWindow as ttkPanedWindow, OptionMenu
from tkinter.filedialog import askopenfilename, asksaveasfilename
from tkinter.simpledialog import Dialog
if system() == 'Darwin':
    from tkmacosx import Button #pyright: ignore
else:
    from tkinter.ttk import Button
from pathlib import Path
from .__about__ import __version__
from .engine import ViewFactorEngine
from .util import managed_directory
import importlib.resources
import os
import json

class ZoneSelection(Dialog):
    def __init__(self, parent, zones, title = None):
         self.zones = zones
         self.selected = []
         super().__init__(parent, title=title)
    def body(self, master):
        super().body(master)
        self.listbox = Listbox(self, selectmode='extended')
        label = Label(self, text="Zones") 
        for i, name in enumerate(self.zones):
            self.listbox.insert(i+1, name)
        label.pack()
        self.listbox.pack()
        return self.listbox
    def apply(self):
        self.selected = [self.listbox.get(idx) for idx in self.listbox.curselection()]

class EnergyPlusViewFactors(Tk):

    @staticmethod
    def name():
        return 'EnergyPlusViewFactors'

    def __init__(self, called_from_ep_cli:bool=False, title:str='EnergyPlus View Factor Calculator',
                 min_width:int=1000, min_height:int=500):
        super().__init__(className=self.name())
        self.title(title)
        if called_from_ep_cli:
            self.option_add('*Dialog.msg.font', 'Helvetica 12')
        self.called_from_ep_cli = called_from_ep_cli
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
        #self.bind('<Key>', self.handle_keypress)
        #self.bind("<FocusIn>", self.handle_focus_in)

    def handle_keypress(self, event) -> None:
        pass

    def handle_focus_in(self, _event) -> None:
        pass

    def gui(self):
        self.file_entry_chars = 80
        self.top_menu()
        self.main = Frame(self, padding=(3, 3, 12, 12))
        self.main.grid(column=0, row=0, sticky=NSEW)
        
        # Set up the internal frames
        self.file_entry()
        self.settings_input()
        self.calculate_interface()

        # Initial coordination between the various parts
        self.update_create_objects()
        self.update_save_intermediates()

        self.columnconfigure(0, weight=1)
        self.rowconfigure(0, weight=1)
        self.main.columnconfigure(0, weight=1)
        self.main.rowconfigure(1, weight=1)

        #height = 500
        #width = 1000
        #x = 128
        #y = 128

        #self.wm_geometry(f"{width}x{height}+{x}+{y}")

    def top_menu(self):
        menubar = Menu(self)

        # File menu
        menu = Menu(menubar, tearoff=False)
        #menu.add_separator()
        menu.add_command(label="Quit", command=self.window_close)
        menubar.add_cascade(label="File", menu=menu)

        # Help menu
        menu = Menu(menubar, tearoff=False)
        #menu.add_command(label="Documentation...", command=self.open_documentation)
        menu.add_command(label="About...", command=self.about_dialog)
        menubar.add_cascade(label="Help", menu=menu)

        self.config(menu=menubar)

    def file_entry(self):
        files = LabelFrame(self.main, text='Files')
        files.grid(column=0, row=0, sticky=NSEW)

        def get_file_input():
            filename = askopenfilename(title='Select input file', filetypes=[('epJSON', '*.epJSON')])
            if filename:
                self.input_file.delete(0, END)
                self.input_file.insert(0, filename)

        Label(files, text='epJSON').grid(column=0, row=0, sticky=EW)
        self.input_file = Entry(files, width=self.file_entry_chars)
        self.input_file.grid(column=1, row=0, sticky=EW)
        Button(files, text='Browse', command=get_file_input).grid(column=2, row=0, sticky=EW)

        def set_output():
            if not self.save_intermediates.get():
                return
            directory = filedialog.askdirectory(parent=self,
                                                    initialdir=os.getcwd(), 
                                                title='Select a directory for View3D output')
            if directory:
                self.output_dir.delete(0, END)
                self.output_dir.insert(0, directory)
            #filename = asksaveasfilename(title='Select View3D output file', filetypes=[('text', '*.txt')])
            #if filename:
            #    self.output_file.delete(0, END)
            #    self.output_file.insert(0, filename)

        Label(files, text='View3D Output').grid(column=0, row=1, sticky=EW)
        self.output_dir = Entry(files, width=self.file_entry_chars)
        self.output_dir.grid(column=1, row=1, sticky=EW)
        Button(files, text='Browse', command=set_output).grid(column=2, row=1, sticky=EW)

        def set_object_output():
            if self.save_intermediates.get() and self.create_objects.get():
                filename = asksaveasfilename(title='Select View3D directory', filetypes=[('text', '*.txt')])
                if filename:
                    self.object_output_file.delete(0, END)
                    self.object_output_file.insert(0, filename)

        Label(files, text='Object Output').grid(column=0, row=2, sticky=EW)
        self.object_output_file = Entry(files, width=self.file_entry_chars)
        self.object_output_file.grid(column=1, row=2, sticky=EW)
        Button(files, text='Browse', command=set_object_output).grid(column=2, row=2, sticky=EW)

        files.columnconfigure(1, weight=1)
    
    def settings_input(self):
        settings = LabelFrame(self.main, text='Settings')
        settings.grid(column=0, row=1, sticky=NSEW)

        self.run_view3d = BooleanVar()
        self.run_view3d.set(False)
        Checkbutton(settings, text='Run View3D', variable=self.run_view3d).grid(column=0, row=0, sticky=EW)

        self.create_objects = BooleanVar()
        self.create_objects.set(False)
        Checkbutton(settings, text='Create EnergyPlus objects', variable=self.create_objects,
                    command=self.update_create_objects).grid(column=0, row=1, sticky=EW)
        
        self.add_objects = BooleanVar()
        self.add_objects.set(False)
        Checkbutton(settings, text='Add EnergyPlus objects to epJSON', variable=self.add_objects).grid(column=0, row=2, sticky=EW)

        self.save_intermediates = BooleanVar()
        self.save_intermediates.set(True)
        Checkbutton(settings, text='Save intermediate files', variable=self.save_intermediates,
                    command=self.update_save_intermediates).grid(column=0, row=3, sticky=EW)

        settings.columnconfigure(0, weight=1)

    def calculate_interface(self):
        #frame = Frame(self.main)
        #frame.grid(column=0, row=2, sticky=NSEW)
        Button(self.main, text='Calculate', command=self.calculate).grid(column=0, row=2, sticky=EW)

        self.columnconfigure(0, weight=1)

    def calculate(self):
        # Check for sufficient input
        input_file = self.input_file.get().strip()
        if not input_file:
            messagebox.showerror('Error', message='Please specify an input file to proceed.')
            return
        else:
            if not os.path.isfile(input_file):
                messagebox.showerror('Error', message=f'Failed to find input file "{input_file}".')
                return
            try:
                with open(input_file, 'r') as fp:
                    data = json.load(fp)
                    zones = list(data.get('Zone', {}).keys())
            except (OSError, json.JSONDecodeError) as error:
                messagebox.showerror('Error', message=f'Failed to read input file: {error}')
                return
            if not zones:
                messagebox.showerror('Error', message=f'Input file "{input_file}" contains no zones.')
                return
        output_dir = None
        if self.save_intermediates.get():
            output_dir = self.output_dir.get().strip()
            if not output_dir:
                messagebox.showerror('Error', message='Please specify a View3D output directory.')
                return
            elif not os.path.isdir(output_dir):
                messagebox.showerror('Error', message=f'View3D output directory "{output_dir}" does not exist.')
                return
        # Do the work
        with managed_directory(output_dir) as dir:
            selector = ZoneSelection(self, zones, title='Select zones')
            if not selector.selected:
                return
            zones = selector.selected
            engine = ViewFactorEngine(data)
            engine.extract(dir, zones)
        messagebox.showinfo('Complete', message=f'Wrote {len(zones)} .vs3 file(s).')

    def update_create_objects(self):
        if not self.create_objects.get():
            self.object_output_file.config(state='disabled')
        else:
            if self.save_intermediates.get():
                self.object_output_file.config(state='normal')

    def update_save_intermediates(self):
        if not self.save_intermediates.get():
            self.output_dir.config(state='disabled')
            #self.object_output_file.config(state='disabled')
        else:
            self.output_dir.config(state='normal')

    def about_dialog(self):
        messagebox.showinfo('About', message = f'This is the {self.title()}, version {__version__}.')

    def run(self):
        self.protocol('WM_DELETE_WINDOW', self.window_close)
        self.mainloop()

    def window_close(self, *_):
        self.destroy()
