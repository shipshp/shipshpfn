#! /usr/bin/env python
# -*- coding: utf-8 -*-

"""\
########################################################################
  Ship-Shape-File-Navigator
########################################################################

Ship-Shape-File-Navigator website: www.shipshapefilenavigator.org
If you find any bugs or have any suggestions you could email to the
project mail list: @shipshapefilenavigator.org

Copyright (C) 2016 Adrian Eirís Torres <adrianet82@gmail.com>

This file is part of Ship-Shape-File-Navigator.

Ship-Shape-File-Navigator is free software: you can redistribute it
and/or modify it under the terms of the GNU General Public License as
published by the Free Software Foundation, either version 3 of the
License, or (at your option) any later version.

Ship-Shape-File-Navigator is distributed in the hope that it will be
useful, but WITHOUT ANY WARRANTY; without even the implied warranty of
MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE.  See the
GNU General Public License for more details.

You should have received a copy of the GNU General Public License
along with this program.  If not, see <http://www.gnu.org/licenses/>.

########################################################################
"""

'''\
gui.py

Widgets GUI, Ship scaffolding
Bindings
(~View)
'''

__version__ = '0.1'

import os

import sys
if sys.version_info[0] > 2:
    #~ TODO: show message-dialog
    print("Ship only runs on python 2.x/<3 versions")

import ConfigParser
import logging

try:
    import Tkinter as tk
    import ttk
except ImportError:
    #~ TODO: show message-dialog
    print "Tkinter module not avaliable. -> install python-tkinter..."
    raise

from tkMessageBox import showwarning as msgbox_warn

import logic
import icons
import styles

import gettext

if __file__ == os.path.basename(__file__):
    SHIP_PATH = "."
else:
    SHIP_PATH = os.path.dirname(__file__)


class App(tk.Tk):
    ''''''
    def __init__(self, parent, devel):
        tk.Tk.__init__(self, parent)
        self.parent = parent
        self.ship_path = SHIP_PATH
        self.initialize()
        #~ Separate initializations allows change language/style just 
        #~ initialization graphical elements.
        self.initialize_ui()
        if devel:
            self.devel_init()
            

    def restart_ui(self):
        self.main_panel.destroy()
        self.statusbar.destroy()
        self.initialize_ui()
        

    def center_window(self, window):
        window.update_idletasks()
        sw = self.winfo_screenwidth()
        rw = window.winfo_width()
        sh = self.winfo_screenheight()
        rh = window.winfo_height()
        xc = (sw - rw) / 2
        yc = (sh - rh) / 2
        window.geometry("+%d+%d" % (xc, yc))


    def init_logging(self):
        logging.basicConfig(level=logging.INFO,
                            filename="%s/%s" %(SHIP_PATH, 'ship.log'),
                            format='%(asctime)s : %(levelname)s : %(message)s',
                            filemode='w')
        logging.info("Starting Ship session")
        

    def add_status_text(self, msg, msgtype='info'):
        self.status_text.insert('end', '\n')
        if msgtype == 'info':
            msg_image = self.iconinfo
        elif msgtype == 'error':
            msg_image = self.iconerror
        #~ FIX: add msgtype to messages
            
        self.status_text.image_create('end', padx=1, image=msg_image)
        self.status_text.insert('end', msg)
        self.status_text.see('end')
        #~ FIX: not loging in status until widget created


    def get_default_confs(self):
        config = ConfigParser.RawConfigParser()
        config.read('%s/%s' % (SHIP_PATH, 'ship.conf'))
        '''\
        TODO: ??? Config file sintax testing.
        '''
        self.configs = config

        self.custom_winconf = config.get("general", "winconf")
        self.custom_treeswidth = config.get("general", "treespanelwidth")
        self.default_language = config.get("general", "default_lang")
        def_homedir = config.get("general", "default_homedir")
        if def_homedir == 'environhomedir':
            try:
                def_homedir = os.environ['HOME']
            except:
                def_homedir = '/'
            
        self.config_default_homedir = def_homedir
        logging.info('Default homedir: %s' % def_homedir)
        #~ TODO: Remove, just for testing logging
        logging.warning("Default home directory not properly set, " +
                        "setting user directory as default.")
        logging.error("Unable to populate table")
        #~ --------------------------------------
        
        try:
            os.listdir(def_homedir)
        except:
            logging.warning(_("Default home directory not properly set, ") +
                            _("setting user directory as default."))
            self.withdraw()
            warning = (_("Ship Default home directory not properly set, ") +
                       _("You can modify it in in menu:\n") +
                       _("Edit -> Preferences."))
            merge = msgbox_warn(_("Ship Default home directory warning"),
                                warning)
            self.config_default_homedir = os.environ['HOME']
            #~ TODO: Set default homedir in config file
            self.deiconify()
            self.center_window(self)
        
        self.default_homedir = self.config_default_homedir
        self.current_dir = self.default_homedir
        self.last_dir = config.get("general", "last_dir")
        
        self.default_history_limit = config.getint("general",
                                                   "history_limit")
        self.default_doubleexts = config.get("general", "doubleexts")
        self.doubleexts = self.default_doubleexts.split(',')
        self.default_shpexts = config.get("shape", "shpexts")
        self.shpexts = self.default_shpexts.split(',')
        self.shp_encoding = config.get("shape", "shp_encoding")
        self.default_shapemode = config.getboolean("shape", "shapemode")
        #~ self.shape_default_tab = config.get("shape", "shape_default_tab")
        
        default_bookmarks = dict(config.items("bookmarks"))
        for key in default_bookmarks.keys():
            default_bookmarks[key] = default_bookmarks[key].split(';')
        
        # Adding sample data bookmark
        if default_bookmarks.has_key('ship_sample_data'):
			test_data_path = '%s/../data-samples' % os.path.abspath(SHIP_PATH)
			test_data_path = os.path.normpath(test_data_path)
			default_bookmarks['ship_sample_data'] = ['Sample data',
													 test_data_path]
        
        self.default_bookmarks = default_bookmarks
        
    def create_default_conf_file(self):
        config = ConfigParser.RawConfigParser()
        sections = ["general", "shape", "bookmarks"]
        for section in sections:
            config.add_section(section)
        
        config_lines = [("general", "winconf", "867x510+257+122"),
                        ("general", "treespanelwidth", 179),
                        ("general", "default_lang", "en"),
                        ("general", "last_dir", "/"),
                        ("general", "default_homedir", "environhomedir"),
                        ("general", "history_limit", 10),
                        ("general", "doubleexts",
                                    "shp,aux,tif,zip,7z,db,sqlite"),
                        ("shape", "shpexts", "dbf,shx,prj,sbn,sbx,cpg,shp.xml,shp.qix,shp.err"),
                        ("shape", "shp_encoding", "utf8"),
                        ("shape", "shapemode", "True"),
                        ("shape", "shape_default_tab", "Table"),
                        ("bookmarks", "ship_sample_data",
                                      "Sample data;../sample-data"),]
        
        for config_line in config_lines:
            config.set(*config_line)
        
        conf_file = '%s/%s' % (SHIP_PATH, 'ship.conf')
        with open(conf_file, 'wb') as configfile:
            config.write(configfile)
        
        
    def set_default_confs(self):
        config_path = os.path.abspath('%s/ship.conf' % SHIP_PATH)
        if not os.path.exists(config_path):
            logging.info("Ship configuration file 'ship.conf' " + 
                         "not exists, creating a new one.")
            self.create_default_conf_file()
        
        self.get_default_confs()
        
        #~ Setting custom app window size
        self.geometry(self.custom_winconf)
        #~ Language
        def_lang_code = self.default_language
        self.set_language(def_lang_code, False)
        self.set_default_homedir(self.default_homedir)
        self.history_limit = self.default_history_limit
        self.shapemode = self.default_shapemode
        #~ TODO: default shape tab: content|table|(view)
        #~ self.shape_default_tab = config.get("shape", "shape_default_tab")
        
        
    def set_language(self, lang_code, restart=True):
        '''\
        FIX: Refresh window to update lang or
             message box: restart to apply
        '''
        locale_folder = "%s/%s" % (SHIP_PATH, "locale")
        if lang_code != 'en':
            lang = gettext.translation("ship",
                                       locale_folder,
                                       languages=[lang_code])
            lang.install()
        else:
            gettext.install("ship", locale_folder)
            
        if restart:
            self.restart_ui()

        
    def set_default_homedir(self, directory):
        self.default_homedir = os.path.abspath(directory)
        self.default_homedir.replace('\\', '/')
    

    def set_scroll(self, tree, axis):
        if axis == 'y':
            direction = 'vertical'
            method = tree.yview
            conf_set = 'yscrollcommand'
            pos = 'right'

        else:
            direction = 'horizontal'
            method = tree.xview
            conf_set = 'xscrollcommand'
            pos = 'bottom'
            
        scroll = ttk.Scrollbar(tree, orient=direction, command=method)
        tree[conf_set] = scroll.set
        scroll.pack(side=pos, fill=axis)


    def initialize(self):
        self.title('Ship-Shape-File-Navigator')
        
        self.init_logging()
        self.set_default_confs()
        
        #~ Creating lists to store directories history
        self.frwddirs = []
        self.backdirs = []
        
        #~ Check tools folder
        tools_folder = "%s/%s" % (SHIP_PATH, 'tools')
        if not os.path.isdir(tools_folder):
            os.mkdir(tools_folder)
            
        #~ Setting styles
        style = styles.Style()
        self.bg_color = style.bg_color
        self.bg_light_color = style.bg_light_color
        self.bg_light2_color = style.bg_light2_color
        self.bg_dark_color = style.bg_dark_color
        self.fg_color = style.fg_color
        self.sel_color = style.sel_color
        self.childwins_bg = self.bg_light_color
        self.childwins_fg = self.fg_color

        #~ Adding iconset ---
        self.appicons = icons.appicons
        self.fileicons = icons.fileicons

        icons_folder = "%s/%s" % (SHIP_PATH, 'icons')
        def load_iconset(iconset):
            for icon in iconset.keys():
                filename = '%s/%s.gif' % (icons_folder, iconset[icon])
                setattr(self, 'icon%s' % icon,
                        tk.PhotoImage(file=filename))
                
        load_iconset(self.appicons)
        load_iconset(self.fileicons)
        
        #~ App main icons
        mainicons = icons.mainicons
        
        for icon in mainicons:
            setattr(self, icon[0],
                    tk.PhotoImage(file="%s/%s.gif" % (icons_folder,
                                                      icon[1])))
        
        #~ app window icon
        try:
            self.tk.call('wm', 'iconphoto', self, self.iconshipbig)
        except Exception, e:
            logging.warning('Not able to set app icon: %s' % e)
        #~ ------------------
        #~ -------------------------------------------------------------
        
        #~ LOGICS instantiations ---------------------------------------
        self.event = logic.GUIEvent(self)
        self.filenav = logic.FileNavigator(self)
        self.fileops = logic.FileOps(self)
        #~ -------------------------------------------------------------
        

    def initialize_ui(self):
        bg_color = self.bg_color
        bg_dark_color = self.bg_dark_color
        bg_light_color = self.bg_light_color
        bg_light2_color = self.bg_light2_color
        fg_color = self.fg_color
        sel_color = self.sel_color

        #~ MENUBAR -----------------------------------------------------
        # toplevel menu ----
        menubar = tk.Menu(self)
        menubar.configure(foreground=fg_color, background=bg_light_color,
                          activebackground=bg_light2_color,
                          activeforeground=fg_color,
                          borderwidth=0)
        
        #~ -------------------------------------------------------------
        #~ # ???: functional menu construc ---
        # Menus ----
        filemenu = tk.Menu(menubar, tearoff=0)
        editmenu = tk.Menu(menubar, tearoff=0)
        viewmenu = tk.Menu(menubar, tearoff=0)
        gomenu = tk.Menu(menubar, tearoff=0)
        bookmarkmenu = tk.Menu(menubar, tearoff=0)
        helpmenu = tk.Menu(menubar, tearoff=0)
        #~ -----------------------------------
         
        # Menuoptions -----
        # menuoption = (image, label, accelerator, command, separator=False)
        
        # File --
        opendiropt = (self.iconopendir, _("Open directory..."), "Ctrl+O",
                      self.event.open_directory, True)
        setsessionhome = (self.iconhometmp,
                          _("Set as session home directory"), "Ctrl+H",
                          self.event.set_as_session_homedir,
                          False)
        setdefaulthome = (self.iconhome,
                          _("Set as default home directory"), "Ctrl+Shift+H",
                          self.event.set_as_default_homedir,
                          True)
        exitappopt = (self.iconexit, _("Exit"), "Ctrl+Q",
                      self.event.close_app, False)
        
        filemenuopts = (opendiropt, setsessionhome, setdefaulthome, exitappopt)
        
        # Edit --
        newfolder = (self.iconfolder, _("New Folder"), "Ctrl+N",
                     self.fileops.new_folder, True)
        cutoption = (self.iconcut, _("Cut"), "Ctrl+X",
                     self.fileops.cut_elements, False)
        copyoption = (self.iconcopy, _("Copy"), "Ctrl+C",
                      self.fileops.copy_elements, False)
        pasteoption = (self.iconpaste, _("Paste"), "Ctrl+V",
                       self.fileops.paste_elements, True)
        selectallopt = (self.iconselall, _("Select All"), "Ctrl+A",
                        self.event.select_all_items, False)
        invertopt = (self.iconselinvert, _("Invert Selection"), "Ctrl+I",
                     self.event.toggle_selection, True) 
        prefsoption = (self.iconprefs, _("Preferences..."), "Ctrl+P",
                       self.event.show_preferences, False)
        
        editmenuopts = (newfolder, cutoption, copyoption, pasteoption,
                        selectallopt, invertopt, prefsoption)
        
        # View --
        bookmarksopt = (self.iconbookmarks, _("Bookmarks"), "Ctrl+B",
                        self.event.get_bookmarks_focus, False)
        dbsopt = (self.icondb, _("Databases"), "Ctrl+G",
                    self.event.get_ddbbs_focus, False)
        toolsopt = (self.icontools, _("Tools"), "Ctrl+T",
                    self.event.get_tools_focus, True)
        treeopt = (self.icontree, _("Focus Tree"), "Alt+1",
                   self.event.get_tree_focus, False)
        conttableopt = (self.iconconttable, _("Focus Content/Table tab"), "Alt+2",
                        self.event.get_list_focus, False)
        contopt = (self.iconcontent, _("Focus Content tab"), "Alt+C",
                   self.event.get_filelist_focus, False)
        tableopt = (self.icontable, _("Focus Table tab"), "Alt+T",
                    self.event.get_table_focus2, False)
        infoopt = (self.icontableinfo, _("Focus Info tab"), "Alt+3",
                   self.event.get_infotab_focus2, False)
        previewopt = (self.iconpreview, _("Focus Preview tab"), "Alt+4",
                      self.event.get_preview_focus2, True)
        #~ splitviewopt ("Split View", "F3")
        shapemodeopt = (self.iconshape, _("Toggle Shape Mode"), "F4",
                        self.event.toggle_shape_mode, False)
        toolbaropt = (self.icontoolbar, _("Toggle Toolbar Panel"), "F8",
                      self.event.toggle_toolbar, False)
        treespanelopt = (self.icontreepanel, _("Toggle Trees Panel"), "F9",
                         self.event.toggle_left_panel, False)

        viewmenuopts = (bookmarksopt, dbsopt, toolsopt, treeopt,
                        conttableopt, contopt, tableopt, infoopt, 
                        previewopt, shapemodeopt, toolbaropt,
                        treespanelopt)

        # Go --
        
        backopt = (self.iconback, _("Back"), "Alt+Left",
                   self.event.go_back, False)
        forwardopt = (self.iconfwrd, _("Forward"), "Alt+Right",
                      self.event.go_frwd, False)
        parentopt = (self.iconup, _("Parent"), "Alt+Up",
                     self.event.go_parent, False)
        homediropt = (self.iconhome, _("Default Home Folder"), "Alt+Home",
                      self.event.go_default_home, False)
        
        gomenuopts = (backopt, forwardopt, parentopt, homediropt)
        
        # Bookmarks --
        
        addbkmrkopt = (self.iconstar, _("Add bookmark"), "Ctrl+D",
                       self.event.add_bookmark, False)
        editbkmrkopt = (self.iconbookmarks, _("Edit bookmarks..."),
                        "Ctrl+Shift+B", self.event.edit_bookmarks, False)
                        
        bookmarkmenuopts = (addbkmrkopt, editbkmrkopt)
        
        # Help --
        
        shiphelpopt = (self.iconhelp, _("Help"), "F1",
                       self.event.get_help_contents, False)
        websiteopt = (self.iconship, _("Website"), "",
                      self.event.get_website, True)
        #~ TODO: "Report Bug" option
        aboutopt = (self.iconinfo, _("About"), "",
                    self.event.show_about, False)
        
        helpmenuopts = (shiphelpopt, websiteopt, aboutopt)
        
        # -----
        
        menugroups = [(_("File"), filemenu, filemenuopts),
                      (_("Edit"), editmenu, editmenuopts),
                      (_("View"), viewmenu, viewmenuopts),
                      (_("Go"), gomenu, gomenuopts),
                      (_("Bookmarks"), bookmarkmenu, bookmarkmenuopts),
                      (_("Help"), helpmenu, helpmenuopts)]

        #~ FIX: for - for to list comprehension ?? (view Toolbar section)
        for menugroup in menugroups:
            for menuoption in menugroup[2]:
                menugroup[1].add_command(image=menuoption[0],
                                         label=menuoption[1],
                                         compound='left',
                                         accelerator=menuoption[2],
                                         command=menuoption[3])
                menugroup[1].configure(foreground=fg_color,
                                       background=bg_light2_color,
                                       activeforeground=fg_color,
                                       activebackground=sel_color
                                       )
                if menuoption[4]:
                    menugroup[1].add_separator()
                    
            menubar.add_cascade(label=menugroup[0], menu=menugroup[1])
            
        # display the menu ---
        self.config(menu=menubar)    
        self.menubar = menubar
    
        #~ END MENUBAR -------------------------------------------------

        #~ PANNED WINDOWS ----------------------------------------------

        main_panel = tk.PanedWindow(self, orient="vertical", sashwidth=0,
                                    borderwidth=0)
        toolbarp = ttk.Frame(main_panel)
        main_windowp = ttk.Frame(main_panel)
        main_panel.add(toolbarp)
        main_panel.add(main_windowp)
        main_panel.pack(fill='both', expand=1)
        self.main_panel = main_panel
        self.toolbar_panel = toolbarp
        self.main_windowp = main_windowp

        main_window = ttk.PanedWindow(main_windowp, orient="vertical")
        upp = ttk.Frame(main_window)
        lwp = ttk.Frame(main_window)
        main_window.add(upp)
        #~ TODO: Status & Terminal
        #~ main_window.add(lwp)
        main_window.pack(fill='both', expand=1)
        
        treeviews_panel = ttk.PanedWindow(upp, orient="horizontal")
        lp = ttk.Frame(treeviews_panel)
        rp = ttk.Frame(treeviews_panel)
        treeviews_panel.add(lp)
        treeviews_panel.add(rp)
        #~ TODO table record navigation panel
        #~ ntrp = ttk.Frame(treeviews_panel)
        #~ treeviews_panel.add(ntrp)
        #~ -------
        treeviews_panel.pack(fill='both', expand=1, pady=2)
        
        self.treeviews_panel = treeviews_panel
        self.lp = lp
        self.rp = rp

        #~ END PANNED WINDOWS ------------------------------------------
        
        #~ TOOLBAR -----------------------------------------------------

        #~ TODO: refactoring: make an unique def for this toolbar and
              #~ the table toolbar
        toolbar = ttk.Frame(toolbarp)
        
        def add_toolbar_button(button):
            button = ttk.Button(toolbar, compound='top', text=button[0],
                                image=button[1], command=button[2])
            button.pack(side='left')
    
        #~ toolbar buttons
        tbb = [(_("Parent"), self.iconup, self.event.go_parent),
               (_("Back"), self.iconback, self.event.go_back),
               (_("Forward"), self.iconfwrd, self.event.go_frwd),
               (_("Home"), self.iconhome, self.event.go_default_home),
               (_("Open"), self.iconopendir, self.event.open_directory),
               (_("Trees Panel"), self.icontreepanel, self.event.toggle_left_panel),
               #~ ("Split View", self.iconship, ),
               (_("Shape Mode"), self.iconshape, self.event.toggle_shape_mode),
               #~ ("Info", self.iconinfo, ),
               #~ ("Terminal", self.iconterm, ),
               ]
    
        map(lambda toolbarbtn: add_toolbar_button(toolbarbtn), tbb)

        toolbar.pack(side='top', fill='both', expand=1)
        
        '''
        #~ TODO: Make shapemode & treespanel checkbuttons:
        
        Changing image:
        cb = tk.Checkbutton(frame, image=self.flagdown,
                     selectimage=self.flagup,
                     indicatoron=0 ) 
        Changing background:
        cb['selectcolor']=cb['background'] # otherwise is red(default)
        cb2 = tk.Checkbutton(frame, image=self.letters,
                      selectcolor='lightgreen',
                      indicatoron=0 )
        '''
        
        #~ END TOOLBAR -------------------------------------------------
        
        treeviews_panel.update_idletasks()
        treeviews_panel.sashpos(0, self.custom_treeswidth)
        
        #~ POPUP MENU --------------------------------------------------
        
        #~ popupmenu = tk.Menu(self, tearoff=0)
        #~ popupmenu.add_command(label=_("Undo"), command=)
        #~ popupmenu.add_command(label=_("Redo"), command=)
        #~ popupmenu.add_command(label=_("Open in new window"), command=)
        #~ popupmenu.add_command(label=_("Rename"), command=)
        #~ self.popupmenu = popupmenu
        
        #~ FIX: to method self.popup (modify binding callbacks):
        #~ def popup(event):
            #~ ''''''
            #~ popupmenu.post(event.x_root, event.y_root)

        #~ self.filetree.bind("<Button-3>", popup)
        #~ FIX: on Mac Button-2 or Ctrl+Button-1?
        
        #~ END POPUP MENU ----------------------------------------------


        #~ STATUS BAR --------------------------------------------------
        
        main_statusbar_label = tk.StringVar()
        status = ttk.Label(self, textvariable=main_statusbar_label,
                           anchor='w', borderwidth=1, relief='sunken',
                           compound='left', image=self.iconinfo)
        status.pack(side='bottom', fill='x')
        self.statusbar = status
        main_statusbar_label.set(_("Toggle Menu: F7, Menu navigation: F10"))
        self.main_statusbar_label = main_statusbar_label

        #~ TODO: action -> toggle status info panel (lwp)
        def toggle_msg_panel(event):
            main_window.add(lwp)
        status.bind('<Button-1>', toggle_msg_panel)
        
        #~ main_window.remove(lwp)
        
        #~ END STATUS BAR ----------------------------------------------
        
        
        #~ LOWER PANEL ------------------------------------------------- 

        n3 = ttk.Notebook(lwp)
        status = ttk.Frame(n3)
        terminal = ttk.Entry(n3)
        n3.add(status, text=_("Status"), image=self.iconinfo, compound='left')
        n3.add(terminal, text=_("Terminal"), image=self.iconterm,
               compound='left')
        n3.pack(fill='both', expand=1)
        self.n3 = n3
        
        #~ Status ---
        status_text = tk.Text(status, relief='sunken', takefocus=0)
        status_text.pack(side='left', expand='y', fill='both')
        status_scrollbar = ttk.Scrollbar(status)
        status_scrollbar.pack(side='right', fill='y')
        status_text['yscrollcommand'] = status_scrollbar.set
        status_scrollbar['command'] = status_text.yview
        status_text.insert('end', 'Starting Ship session')
        
        self.status_text = status_text
        
        #~ TODO: scroll ?
        
        #~ Terminal ---
        terminal_text = tk.Text(terminal, relief='sunken', takefocus=0)
        terminal_text.pack(side='left', expand='y', fill='both')
        terminal_scrollbar = ttk.Scrollbar(terminal)
        terminal_scrollbar.pack(side='right', fill='y')
        terminal_text['yscrollcommand'] = terminal_scrollbar.set
        terminal_scrollbar['command'] = terminal_text.yview
        terminal_text.insert('end', '[Console]')
        #~ System terminal:
        #~ TODO: Thread-safe console,
        #~       fit xterm to widget, initial script-set variables,
        #~       GUI interaction...
        #~ terminal.pack(fill='both', expand=1, pady=2)
        #~ terminal.update()
        #~ terminal_id = terminal.winfo_id()
        #~ terminal_w = terminal.winfo_width()
        #~ terminal_h = terminal.winfo_height()
        #~ os.system('xterm -rightbar -into %d -geometry %sx%s -sb &' % (terminal_id,
                                                           #~ terminal_w/6,
                                                           #~ terminal_h/13 ))
        #~ ------------
        
        #~ TODO: scroll ?
        #~ self.set_scroll(widget, 'y')
        
        
        #~ UPPER PANEL ------------------------------------------------
        
        #~ Notebook 1 (Filetree, Tooltree) -----------------------------
        
        n1 = ttk.Notebook(lp)
        bookmarks = ttk.Frame(n1)
        tree = ttk.Frame(n1)
        ddbbs = ttk.Frame(n1)
        tools = ttk.Frame(n1)
        n1.add(bookmarks, text='', image=self.iconbookmarks, compound='left')
        n1.add(tree, text=_('Tree'), image=self.icontree, compound='left')
        n1.add(ddbbs, text=_('DBs'), image=self.icondb, compound='left')
        n1.add(tools, text=_('Tools'), image=self.icontools, compound='left')
        n1.pack(side='left', fill='both', expand=1)
        self.n1 = n1
        
        n1.bind('<<NotebookTabChanged>>', self.event.select_tree_tab)
        
        #~ Bookmarks ---
        self.bookmarks = ttk.Treeview(bookmarks, columns=("path"),
                                      displaycolumns="",
                                      selectmode="browse",
                                      #~ show='tree',
                                      style="Ftree.Treeview")
        #~ self.bookmarks.heading('#0', text='Bookmarks')
        self.filenav.populate_bookmarks_tree()
        
        self.bookmarks.bind('<<TreeviewOpen>>', self.filenav.exec_bookmark)
        self.bookmarks.bind('<<TreeviewSelect>>', self.filenav.select_bookmark)
        #~ self.bookmarks.bind('<FocusOut>', self.filenav.exec_bookmark)
        
        self.set_scroll(self.bookmarks, 'y')
        
        #~ Filetree ---
        def filetree_path_add_dirs():
            '''
            Adding paths to filetree_path entry when combobox is
            expanded.
            '''
            #~ FIX: ? Sort list
            paths = list(set(self.backdirs + self.frwddirs))
            self.filetree_path_entry['values'] = paths
            
        filetree_path_entry = ttk.Combobox(tree, state='readonly',
                                           exportselection=0,
                                           postcommand=filetree_path_add_dirs)
        filetree_path_entry.pack(side='top', fill='x', pady=1)
        self.filetree_path_entry = filetree_path_entry
        #~ filetree_path_entry.bind("<Return>", )
        
        filetree = ttk.Treeview(tree, columns=("path", "type"), 
                                displaycolumns="", selectmode="browse",
                                show='tree', style="Ftree.Treeview")
        filetree.tag_configure('shp_err', image=self.iconship)
        
        self.rootdir = self.current_dir
        self.filenav.set_tree_root(filetree, self.rootdir)
        
        filetree.bind('<<TreeviewOpen>>', self.filenav.exec_filetree_item)
        filetree.bind('<<TreeviewSelect>>', self.filenav.update_list)
        self.filetree = filetree
        
        self.set_scroll(self.filetree, 'y')
        
        # files mode show/hide selector
        #~ TODO: Way to Hide/Show file types in filetree. Panel/Preferences?
        
        #~ filesmode_bar = ttk.Frame(tree)
        #~ def add_filesmodebar_button(button):
            #~ b = ttk.Button(filesmode_bar, image=button[1], command=button[2])
            #~ b.pack(side='left')
        #~ 
        #~ filesmode_buttons = [("Record #", self.iconship, self.event.go_parent),
                             #~ ("Table Edit", self.icontableedit, self.event.go_parent),
                             #~ ("Forward", self.iconfwrd, self.event.go_parent),
                             #~ ("Home", self.iconhome, self.event.go_default_home),
                             #~ ("Open Directory", self.iconopendir, self.event.open_directory),
                             #~ ("Trees Panel", self.icontreepanel, self.event.go_parent),
                             #~ ("Split View", self.iconship, self.event.go_parent),
                             #~ ("Shape Mode", self.iconshape, self.event.toggle_shape_mode),
                             #~ ("Tools", self.iconship, self.event.go_parent),
                             #~ ("Console", self.iconship, self.event.go_parent)]
        #~ 
        #~ for filesmode_button in filesmode_buttons:
            #~ add_filesmodebar_button(filesmode_button)
        #~ 
        #~ filesmode_bar.pack(side='bottom', fill='x')
        
        #~ filesmode_text = tk.StringVar()
        #~ filesmode_selector = ttk.Label(tree, borderwidth=1,
                                       #~ textvariable=filesmode_text,
                                       #~ relief='sunken')
        #~ filesmode_selector.pack(side='bottom', fill='x')
        #~ shpmode_btn = ttk.Button(filesmode_selector, 
                                #~ image=self.iconshp)
                                #~ command=)
        #~ shpmode_btn.pack(side='left', padx=3)
        #~ tablemode_btn = ttk.Button(filesmode_selector, 
                                   #~ image=self.icontable)
                                   #~ command=)
        #~ tablemode_btn.pack(side='left', padx=3)
        #~ rastermode_btn = ttk.Button(filesmode_selector, 
                                   #~ image=self.icontable)
                                   #~ command=)
        #~ rastermode_btn.pack(side='left', padx=3)
        
        #~ DBtree ---
        self.dbtree = ttk.Treeview(ddbbs, selectmode="browse",
                                   style="Ftree.Treeview")
        #~ self.filenav.populate_ddbbs()
        self.set_scroll(self.dbtree, 'y')
        
        #~ Tooltree ---
        self.tooltree = ttk.Treeview(tools, selectmode="browse",
                                     style="Ftree.Treeview")
        self.filenav.populate_tools()
        self.set_scroll(self.tooltree, 'y')

        #~ Notebook 2 (Content, Table, Info, Preview, ...) -------------

        n2 = ttk.Notebook(rp)
        content = ttk.Frame(n2)
        table = ttk.Frame(n2)
        info = ttk.Frame(n2)
        preview = tk.Frame(n2)
        projinfo = tk.Frame(n2)
        n2.add(content, text=_('Content'), image=self.iconcontent,
               compound='left')
        n2.add(table, text=_('Table'), image=self.icontable,
               compound='left', state='hidden')
        n2.add(info, text=_('Info'), image=self.icontableinfo,
               compound='left', state='hidden')
        n2.add(preview, text=_('Preview'), image=self.iconpreview,
               compound='left', state='hidden')
        n2.add(projinfo, text=_('Project info'), image=self.icontableinfo,
               compound='left', state='hidden')
        n2.pack(side='left', fill='both', expand=1)
        self.tableframe = table
        self.n2 = n2

        n2.bind('<<NotebookTabChanged>>', self.event.select_content_tab)
        
        #~ Filelist ---
        filelist_path = tk.StringVar()
        self.filelist_path_entry = ttk.Entry(content,
                                             textvariable=filelist_path)
        self.filelist_path_entry.pack(side='top', fill='x')
        self.filelist_path_entry.bind('<FocusIn>',
                                      self.event.get_filelist_path_entry_focus)
        
        self.filelist = ttk.Treeview(content,
                                     columns=('path','type','size',
                                              'modified', 'treenode'),
                                     displaycolumns=("size", "modified"),
                                     selectmode="extended",
                                     style="Flist.Treeview")
        self.filelist.heading('#0', text=_('Name'))
        self.filelist.heading('size', text=_('Size'))
        self.filelist.column('size', width=100, anchor='e')
        self.filelist.heading('modified', text=_('Modified'))
        
        self.content_statusbar_label = tk.StringVar()
        self.content_statusbar = ttk.Label(content, 
                                           textvariable=self.content_statusbar_label,
                                           borderwidth=1, relief='sunken',
                                           anchor='w')
        self.content_statusbar.pack(side='bottom', fill='x')
        
        '''\
        self.filenav.populate_list('root')

        There's no need to populate_list here, it's populated on init
        because of <<TreeviewSelect>> event, but noted here for the sake
        of readability. 
        filetree TreeviewSelect -> event.update_list -> event.populate_list
        '''
        
        self.filelist.bind('<<TreeviewSelect>>', self.event.select_filelist_item)
        
        self.set_scroll(self.filelist, 'y')
        
        #~ Table ---
        
        self.tablelist = ttk.Treeview(table, style="Table.Treeview",
        #~ TODO: table items selection
                                      #~ selectmode="extended")
                                      selectmode="browse")
        self.tablelist.heading("#0", text="#",
                               command=self.event.select_table_column)
        self.tablelist.column("#0", width=55, stretch='False')
        
        table_bar_bottom = ttk.Frame(table)
        table_bar_bottom.pack(side='bottom', fill='x')
        
        self.table_statusbar_label = tk.StringVar()
        self.table_statusbar = ttk.Label(table_bar_bottom, 
                                         textvariable=self.table_statusbar_label,
                                         borderwidth=1, relief='sunken',
                                         anchor='w', width=35)
        self.table_statusbar.pack(side='left', fill='y')
        
        self.tablelist_yscroll = ttk.Scrollbar(table, orient='vertical')
        self.tablelist_xscroll = self.set_scroll(self.tablelist, 'x')

        #~ Simple table navigator --------
        table_navigator = ttk.Frame(table_bar_bottom)
        table_navigator.pack(side='left', fill='x', padx=10)
        
        #~ --- table navigator buttons
        first_rec = tk.Button(table_navigator, image=self.iconsetfirst,
                              command=self.event.select_table_first_item,
                              bd=2, height=11, width=11, bg=bg_light_color)
        first_rec.pack(side='left', padx=3)
        
        prev_rec = tk.Button(table_navigator, image=self.iconsetprev,
                             command=self.event.do_prev_step,
                             #~ state='disabled',
                             bd=2, height=11, width=11, bg=bg_light_color)
        prev_rec.pack(side='left', padx=3)
        self.prev_rec_btn = prev_rec
        #~ --- table navigator search box
        navigator_chooser = tk.IntVar()
        self.table_navigator_entry = ttk.Entry(table_navigator, width=10,
                                               textvariable=navigator_chooser,
                                               justify='center')
        self.table_navigator_entry.pack(side='left', fill='x')
        navigator_chooser = ''
        self.navigator_chooser = navigator_chooser
        self.table_navigator_entry.insert('end', navigator_chooser)
        
        self.table_navigator_entry.bind("<Return>",
                                        self.event.go_to_table_item)
        
        next_rec = tk.Button(table_navigator, image=self.iconsetnext,
                             command=self.event.do_next_step,
                             #~ state='disabled',
                             bd=2, height=11, width=11, bg=bg_light_color)
        next_rec.pack(side='left', padx=3)
        self.next_rec_btn = next_rec
        
        last_rec = tk.Button(table_navigator, image=self.iconsetlast,
                              command=self.event.select_table_last_item,
                              bd=2, height=11, width=11, bg=bg_light_color)
        last_rec.pack(side='left', padx=3)
        #~ --- step
        step_text = _("Step")
        step_label = ttk.Label(table_navigator, text=step_text)
        step_label.pack(side='left', padx=10)
        
        #~ self.table_step_spinbox = tk.Spinbox(table_navigator, width=5,
                                           #~ from_=1, to=10,
                                           #~ justify='center')
        #~ self.table_step_spinbox.pack(side='left', fill='y')
        
        step_value = tk.IntVar()
        self.table_step_entry = ttk.Entry(table_navigator, width=7,
                                          textvariable=step_value,
                                          justify='center')
        self.table_step_entry.pack(side='left', fill='y')
        step_value = 1
        self.step_value = step_value
        self.table_step_entry.insert('end', step_value)
        
        self.table_step_entry.bind('<FocusOut>', self.event.get_step_value)
        self.table_step_entry.bind('<Return>', self.event.confirm_step_value)
        
        #~ --- auto
        #~ autostep_text = _("Auto")
        #~ autostep_label = ttk.Label(table_navigator, text="%s (ms)" % (autostep_text))
        #~ autostep_label.pack(side='left', padx=10)
        
        #~ autostep_switch = tk.Button(table_navigator, text='Auto',
                                    #~ font=('Sans', 8), height=1,
                                    #~ command=self.event.do_next_step,
                                    #~ activebackground=bg_light_color,
                                    #~ bd=0, pady=0, padx=2,
                                    #~ bg=bg_light_color)
        #~ autostep_switch.pack(side='left', fill='x', padx=10)
        #~ self.autostep_switch = autostep_switch
        
        #~ autostep_switch = ttk.Checkbutton(table_navigator, text='Auto',
                                          #~ command=self.event.autostep)
        #~ autostep_switch.pack(side='left', fill='x', padx=10)
        #~ self.autostep_switch = autostep_switch
        
        #~ autostep_values = ['off', 1, 10, 100, 500, 1000, 2000, 5000]
        #~ autostep_delay_combo = ttk.Combobox(table_navigator, width=5,
                                            #~ justify='center',
                                            #~ exportselection=0,
                                            #~ values=autostep_values)
        #~ autostep_delay_combo.pack(side='left', fill='y', padx=3)
        #~ autostep_delay_combo.current(0)
        #~ self.autostep_values = autostep_values
        #~ self.autostep_delay_combo = autostep_delay_combo
        #~ ---
        
        #~ -------------------------------
        #~ TABLE TOOLBAR -----------------------------------------------
        #~ toolbar = ttk.Frame(table)
        #~ 
        #~ def add_toolbar_button(button):
            #~ b = ttk.Button(toolbar, image=button[1], command=button[2])
            #~ b.pack(side='left')
        #~ 
        #~ toolbar_buttons = [("Record #", self.iconship, self.event.go_parent),
                            #~ #self.tablelist['show'] = 'headings'
                            #~ #self.tablelist['show'] = 'tree headings'
                           #~ ("Table Edit", self.icontableedit, self.event.go_parent),
                           #~ ("Forward", self.iconfwrd, self.event.go_parent),
                           #~ ("Home", self.iconhome, self.event.go_default_home),
                           #~ ("Open Directory", self.iconopendir, self.event.open_directory),
                           #~ ("Trees Panel", self.icontreepanel, self.event.go_parent),
                           #~ ("Split View", self.iconship, self.event.go_parent),
                           #~ ("Shape Mode", self.iconshape, self.event.toggle_shape_mode),
                           #~ ("Tools", self.iconship, self.event.go_parent),
                           #~ ("Console", self.iconship, self.event.go_parent)]
        #~ 
        #~ for toolbar_button in toolbar_buttons:
            #~ add_toolbar_button(toolbar_button)
        #~ 
        #~ toolbar.pack(side='top', fill='x')
        #~ END TABLE TOOLBAR -------------------------------------------

        #~ Info ----------
        infotab = tk.Canvas(info)
        infotab.pack(side='left', fill='both', expand=1, padx=5, pady=5)
        
        infotab_file = ttk.Frame(infotab)
        infotab_file.pack(side='top', fill='both', expand=1)
        self.infotab_file = infotab_file
        
        self.geofile_name_var = tk.StringVar()
        geofile_name = ttk.Label(infotab_file,
                                 textvariable=self.geofile_name_var,
                                 #~ compound='left', image=self.iconinfo,
                                 background=sel_color,
                                 foreground=self.childwins_fg,
                                 font='Verdana 16 bold', anchor='nw')
        geofile_name.pack(side='top', fill='x')
        
        self.geofile_type_var = tk.StringVar()
        geofile_type = ttk.Label(infotab_file,
                                 textvariable=self.geofile_type_var,
                                 #~ compound='left', image=self.iconinfo,
                                 anchor='nw')
        geofile_type.pack(side='top', fill='x', padx=30, pady=10)
        
        self.geofile_srs_var = tk.StringVar()
        geofile_srs = ttk.Label(infotab_file,
                                 textvariable=self.geofile_srs_var,
                                 compound='left', image=self.iconprj,
                                 anchor='nw')
        geofile_srs.pack(side='top', fill='x', padx=30, pady=10)
        
        self.geofile_srsmsg_var = tk.StringVar()
        geofile_srsmsg = tk.Message(infotab_file, width=600,
                                    textvariable=self.geofile_srsmsg_var)
        geofile_srsmsg.pack(side='top', fill='x', padx=30, pady=10)
        
        geofile_fields_schema_title = ttk.Label(infotab_file,
                                 text=_("Fields schema:"), anchor='nw')
        geofile_fields_schema_title.pack(side='top', fill='x',
                                        padx=30, pady=10)
        
        geofile_fields_schema = ttk.Treeview(infotab_file, 
                                             columns=('field','type'),
                                             selectmode='browse')
        geofile_fields_schema.heading('#0', text='#')
        geofile_fields_schema.column('#0', width=50, anchor='center')
        geofile_fields_schema.heading('field', text=_("FIELD"))
        geofile_fields_schema.column('field', width=100)
        geofile_fields_schema.heading('type', text=_("TYPE"))
        geofile_fields_schema.column('type', width=100, anchor='center')
        geofile_fields_schema.pack(side='left', fill='y', padx=30, pady=5)
        self.geofile_fields_schema = geofile_fields_schema
        
        geofile_fields_stats = tk.Canvas(infotab_file, bg=bg_color)
        geofile_fields_stats.pack(side='left', padx=30, pady=5,
                                  fill='y')
        geofile_fields_stats.color = sel_color
        geofile_fields_stats.color_fg = fg_color
        self.geofile_fields_stats = geofile_fields_stats
        
        infotab.bind('<FocusIn>', self.event.get_infotab_focus)
        self.infotab = infotab
        #~ ---------------
        
        #~ Preview -------
        preview['bg'] = bg_color
        coords_color = 'red'
        geoms_color = '#ABC7F0'

        #~ Preview statusbar
        preview_statusbar = ttk.Frame(preview)
        preview_statusbar.pack(side='bottom', fill='both')
        
        self.preview_statusbar_label_var = tk.StringVar()
        preview_statusbar_label = ttk.Label(preview_statusbar, 
                                            textvariable=self.preview_statusbar_label_var,
                                            borderwidth=1, relief='sunken',
                                            width=-25, anchor='w')
        preview_statusbar_label.pack(side='left', fill='both')

        pb_style = ttk.Style()
        pb_style_name = 'ship_pb.Horizontal.TProgressbar'
        self.pb_bg_color = bg_dark_color
        self.pb_end_color = bg_color
        pb_style.configure(pb_style_name, background=sel_color,
                           troughcolor=bg_color)
        self.pb_value = tk.IntVar()
        preview_pb = ttk.Progressbar(preview_statusbar,
                                     style=pb_style_name, 
                                     variable=self.pb_value)
        preview_pb.pack(side='bottom', fill='x', expand=1)
        self.pb_style = pb_style
        self.preview_pb = preview_pb

        #~ Coordinates labels
        coordsfont = ('Sans', 8)
        #~ Coords up
        preview_coords_up = tk.Frame(preview, bg=bg_color)
        preview_coords_up.pack(side='top', fill='x', padx=5, pady=5)
        self.preview_coords_label_up_l = tk.StringVar()
        coords_label_up_l = ttk.Label(preview_coords_up, 
                                        textvariable=self.preview_coords_label_up_l,
                                        relief='flat', anchor='w',
                                        foreground=coords_color, background=bg_color,
                                        font=coordsfont)
        self.preview_coords_label_up_r = tk.StringVar()
        coords_label_up_r = ttk.Label(preview_coords_up, 
                                        textvariable=self.preview_coords_label_up_r,
                                        relief='flat', anchor='e',
                                        foreground=coords_color, background=bg_color,
                                        font=coordsfont)
        coords_label_up_l.pack(side='left')
        coords_label_up_r.pack(side='right')
        #~ Coords down
        preview_coords_dn = tk.Frame(preview, bg=bg_color)
        preview_coords_dn.pack(side='bottom', fill='x', padx=5, pady=5)
        self.preview_coords_dn = preview_coords_dn
        self.preview_coords_label_dn_l = tk.StringVar()
        coords_label_dn_l = ttk.Label(preview_coords_dn,
                                        textvariable=self.preview_coords_label_dn_l,
                                        relief='flat', anchor='w',
                                        foreground=coords_color, background=bg_color,
                                        font=coordsfont)
        self.preview_coords_label_dn_r = tk.StringVar()
        coords_label_dn_r = ttk.Label(preview_coords_dn, 
                                        textvariable=self.preview_coords_label_dn_r,
                                        relief='flat', anchor='e',
                                        foreground=coords_color, background=bg_color,
                                        font=coordsfont)
        coords_label_dn_l.pack(side='left')
        coords_label_dn_r.pack(side='right')

        #~ Canvas
        preview_canvas = tk.Canvas(preview, bg=bg_color, highlightthickness=0)
        preview_canvas.color = geoms_color
        preview_canvas.pack(side='left', fill='both', expand=1, padx=4)
        
        #~ preview_canvas.bind('<FocusIn>', self.event.get_preview_focus)
        preview_canvas.bind('<FocusOut>', self.filenav.stop_draw_preview)
        self.preview_canvas = preview_canvas
        #~ ---------------
        
        #~ Project Info ----
        projinfotab = tk.Canvas(projinfo)
        projinfotab.pack(side='left', fill='both', expand=1)
        
        projinfotab_file = ttk.Frame(projinfotab)
        projinfotab_file.pack(side='top', fill='both', expand=1)
        self.projinfotab_file = projinfotab_file
        
        geoprojfile_layers_schema = ttk.Treeview(projinfotab_file, 
                                                 selectmode='browse')
        geoprojfile_layers_schema.heading('#0', text='TOC')
        geoprojfile_layers_schema.column('#0', width=300)
        geoprojfile_layers_schema.pack(side='left', fill='y', padx=30, pady=30)
        self.geoprojfile_layers_schema = geoprojfile_layers_schema
        
        #~ geofile_fields_stats = tk.Canvas(infotab_file, bg=bg_color)
        #~ geofile_fields_stats.pack(side='left', padx=30, pady=5,
                                  #~ fill='y')
        #~ geofile_fields_stats.color = sel_color
        #~ geofile_fields_stats.color_fg = fg_color
        #~ self.geofile_fields_stats = geofile_fields_stats
        
        #~ projinfotab.bind('<FocusIn>', self.event.get_projinfotab_focus)
        self.projinfotab = projinfotab
        #~ ---------------
        
        #~ KEY BINDINGS ------------------------------------------------
        
        '''\
        TODO: Escape popup menu
        def hide_popup(event):
            #~ popup active?
            self.popupmenu.destroy()
        self.bind_class('<Escape>', hide_popup)
        '''
        
        '''\
        FIX: bind all for events that may be necessary with other
        no-Topwindow windows (F1,?...)
        self.bind_all
        '''
        
        #~ Menu events:
        #~ Also Alt+B to focus bookmarks
        self.bind('<Control-b>', self.event.get_bookmarks_focus)
        self.bind('<Control-Shift-KeyPress-B>', self.event.edit_bookmarks)
        self.bind('<Control-d>', self.event.add_bookmark)
        self.bind('<Control-g>', self.event.get_ddbbs_focus)
        self.bind('<Control-h>', self.event.set_as_session_homedir)
        self.bind('<Control-Shift-KeyPress-H>', self.event.set_as_default_homedir)
        self.bind('<Control-l>', self.event.focus_table_navigator)
        self.bind('<Control-n>', lambda x: self.fileops.new_folder())
        self.bind('<Control-o>', lambda x: self.event.open_directory())
        self.bind('<Control-p>', lambda x: self.event.show_preferences())
        self.bind('<Control-q>', lambda x: self.event.close_app())
        self.bind('<Control-s>', self.event.focus_table_step)
        self.bind('<Control-t>', self.event.get_tools_focus)
        #~ ---------
        #~ self.bind('<Control-x>'...
        self.bind('<<Cut>>', self.fileops.cut_elements)
        #~ self.bind('<Control-c>'...
        self.bind('<<Copy>>', self.fileops.copy_elements)
        #~ self.bind('<Control-v>'...
        self.bind('<<Paste>>', self.fileops.paste_elements)
        #~ ---------
        
        self.bind('<Alt-KeyPress-1>', self.event.get_tree_focus)
        '''
        Alt-2 bind from menus/filetree focus -> filelist 1st visible
        tab: content or table.
        '''
        #~ self.bind('<Alt-KeyPress-2>', )
        #~ self.bind('<Alt-KeyPress-2>', lambda x: self.event.get_list_focus())
        self.bind('<Alt-b>', self.event.get_bookmarks_focus)
        self.bind('<Alt-c>', self.event.get_filelist_focus)
        self.bind('<Alt-t>', self.event.show_shape_table)
        
        self.bind('<Alt-KeyPress-3>', self.event.get_infotab_focus)
        self.bind('<Alt-KeyPress-4>', self.event.get_preview_focus)

        self.bind('<Alt-Left>', lambda x: self.event.go_back())
        self.bind('<Alt-Right>', lambda x: self.event.go_frwd())
        self.bind('<Alt-Up>', lambda x: self.event.go_parent(True))
        self.bind('<Alt-Home>', lambda x: self.event.go_default_home())
        
        self.bind('<Shift-R>', lambda x: self.event.get_tree_focus())
        
        self.bind('<F1>', lambda x: self.event.get_help_contents())
        self.bind('<F4>', lambda x: self.event.toggle_shape_mode())
        self.bind('<F7>', self.event.toggle_menubar)
        self.bind('<F8>', self.event.toggle_toolbar)
        self.bind('<F9>', self.event.toggle_left_panel)
        
        #~ Filetree ----
        self.filetree.bind('<Home>', self.event.select_first_item)
        self.filetree.bind('<Control-Up>', self.event.select_first_item)
        self.filetree.bind('<End>', self.event.select_last_item)
        self.filetree.bind('<Control-Down>', self.event.select_last_item)
        self.filetree.bind('<Control-space>', self.event.get_bookmarks_focus)
        #~ Alt-2 bind from filelist -> focus table.

        #~ Combobox
        self.filetree_path_entry.bind('<<ComboboxSelected>>',
                                      self.filenav.update_filetree_path_entry)
        self.filetree.bind('<FocusIn>', self.event.unfocus_table_navigator_reset)
        
        #~ Filelist ----
        self.filelist.bind('<Home>', self.event.select_first_item)
        self.filelist.bind('<Control-Up>', self.event.select_first_item)
        self.filelist.bind('<End>', self.event.select_last_item)
        self.filelist.bind('<Control-Down>', self.event.select_last_item)
        self.filelist.bind('<Control-a>', self.event.select_all_items)
        self.filelist.bind('<Control-i>', self.event.toggle_selection)
        self.filelist.bind('<Alt-2>', self.event.get_table_focus)
        self.filelist.bind('<F2>', self.fileops.rename_elements)
        self.filelist.bind('<Delete>', self.fileops.delete_elements)
        self.filelist.bind('<<TreeviewOpen>>', self.filenav.exec_filelist_item)
        '''\
        FIX: Change behaviour: Space(->TreeviewOpen) toggles shapetable/list view
              not open a file navigator
              -> Space in list view focus to treelist
        TODO: if shape
        self.filelist.bind('<<TreeviewOpen>>', self.event.show_shape_table)
        '''
        
        #~ Table ----
        self.tablelist.bind('<Home>', self.event.moveto_table_first_item)
        self.tablelist.bind('<Control-Up>', self.event.select_table_first_item)
        self.tablelist.bind('<End>', self.event.moveto_table_last_item)
        self.tablelist.bind('<Control-Down>', self.event.select_table_last_item)
        self.tablelist.bind('<Up>', self.event.select_table_prev_item)
        self.tablelist.bind('<Down>', self.event.select_table_next_item)
        self.tablelist.bind('<Prior>', self.event.moveto_table_prev_page)
        self.tablelist.bind('<Next>', self.event.moveto_table_next_page)
        self.tablelist.bind('<Control-a>', self.event.select_all_items)
        self.tablelist.bind('<Control-i>', self.event.toggle_selection)
        self.tablelist.bind('<Control-Left>', self.event.do_prev_step)
        self.tablelist.bind('<Control-Right>', self.event.do_next_step)
        
        '''
        FIX: Add MouseWheel event
             Linux:   '<Button-4/5>' -> .num
             Win/Mac: '<MouseWheel>' -> .delta
        '''
        self.tablelist.bind('<Button-4>',
                            self.event.moveto_table_prev_page)
        self.tablelist.bind('<Control-Button-4>',
                            self.event.select_table_prev_item)
        self.tablelist.bind('<Button-5>',
                            self.event.moveto_table_next_page)
        self.tablelist.bind('<Control-Button-5>',
                            self.event.select_table_next_item)
            
        self.tablelist.bind('<space>', lambda x: self.event.get_tree_focus())
        #~ TODO: On active tablelist item -> edit record with table records navigator (opens panel)
        #~ self.tablelist.bind('<<TreeviewOpen>>', self.event.active_table_item)
        self.tablelist.bind('<<TreeviewSelect>>', self.event.select_table_items)
        
        self.tablelist.bind('<Right>',
                            lambda x: self.tablelist.xview(tk.SCROLL,
                                                           25,
                                                           tk.UNITS))
        self.tablelist.bind('<Left>',
                            lambda x: self.tablelist.xview(tk.SCROLL,
                                                           -25,
                                                           tk.UNITS))
        
        self.tablelist.bind('<Configure>', self.event.on_resize)
        
        #~ Key bindings notes: ----
        #~ Capital Key -> Control + Shift + I
        #~ self.bind('<Control-I>', self.event.get_tree_focus)
        #~ Get rid bindings of a widget
        #~ text.bind("<Return>", lambda e: None)
        #~ ---
        #~ ENDKEY BINDINGS ---------------------------------------------
        
        self.protocol("WM_DELETE_WINDOW", self.event.close_app)
        

    def devel_init(self):
        print "---------------"
        print "Ship devel mode"
        print "---------------"
        
        #~ Opening a folder:
        #~ folder = ''
        #~ self.event.change_rootdir(folder)
        #~ -----------------
        
        #~ Selecting a filetree item:
        #~ item_name = 'root'
        #~ self.filetree.focus(item_name)
        #~ self.filetree.event_generate('<<TreeviewClose>>')
        #~ self.populate_list(item_name)
        #~ --------------------------


def main(devel=False):
    app = App(None, devel)
    app.mainloop()
    

def profiling():
    import cProfile
    import pstats
    #~ cProfile.run('main()')
    stats_file = '%s/%s' % (SHIP_PATH, 'profiling')
    cProfile.run('main(True)', stats_file)
    p = pstats.Stats(stats_file)
    #~ p.strip_dirs().sort_stats(-1).print_stats()
    #~ p.sort_stats('name')
    #~ p.print_stats()
    p.sort_stats('cumulative').print_stats(10)

    
if __name__ == "__main__":
    #~ profiling()
    main()
