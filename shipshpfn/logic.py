#! /usr/bin/env python
# -*- coding: utf-8 -*-

'''\
logic.py
Event handling
File Navigator (populate trees, lists, ...)
(~Controler)
'''

import os
import shutil
import time
import logging

import Queue
import threading

from re import match as re_match
from glob import glob
from webbrowser import open as webbrowser_open
from platform import system as platform_system
from zipfile import ZipFile as zipfile
from tempfile import mkdtemp as temp_mkdtemp
from xml.dom.minidom import parse as dom_parse

import Tkinter as tk
import ttk
import tkFileDialog as filedialog
import tkSimpleDialog as simpledialog
import tkMessageBox as messagebox

import shape
import shapedb
import tables


class GUIEvent():
    ''''''
    def __init__(self, parent):
        self.parent = parent
        self.autostep_stop_flag = False

    def select_all_items(self, event=None):
        if event:
            wdgt = event.widget
        
        else:
            wdgt = self.parent.filelist
            
        wdgt.selection_add(wdgt.get_children())

    def select_filelist_item(self, event):
        wdgt = event.widget
        sel_item = wdgt.selection()
        items_sel = len(sel_item)

        list_label = self.parent.content_statusbar_label
        list_label_elmts = list_label.get().split(',')[0]
        selected_text = _("selected")
        
        n2 = self.parent.n2
        
        if items_sel == 1:
            sel_item = sel_item[0]
            item_path = wdgt.item(sel_item)['values'][0]
            item_type = wdgt.item(sel_item)['values'][1]
            item_name = os.path.basename(item_path)

            #~ Show/Hide table tab if/ifnot shapefile
            if item_type == 'shape':
                self.set_tab_state(n2, 'normal', 0, 1, 2, 3)
                self.set_tab_state(n2, 'hidden', 4)
                
            elif item_type == 'sqliteshp' \
            or item_type == 'csv':
                self.set_tab_state(n2, 'normal', 1)
                self.set_tab_state(n2, 'hidden', 2, 3, 4)
                
            else:
                self.set_tab_state(n2, 'hidden', 1, 2, 3, 4)

            #~ Setting path label
            self.parent.filelist_path_entry.delete(0, 'end')
            self.parent.filelist_path_entry.insert('end', item_path)
            list_label_text = '"%s" %s' % (item_name, selected_text)
            
        else:
            list_label_text = "%s %s %s" % (items_sel, _("items"),
                                            selected_text)
            
        list_label.set("%s, %s" %(list_label_elmts, list_label_text))
        
    def select_first_item(self, event):
        wdgt = event.widget
        first_item = wdgt.get_children()[0]
        
        wdgt.selection_set(first_item)
        wdgt.focus(first_item)
        wdgt.see(first_item)
        
    def select_last_item(self, event):
        wdgt = event.widget
        childrens = wdgt.get_children
        first_item = childrens()[0]
        
        items_no = len(childrens())
        
        if items_no == 1 \
        and wdgt.item(first_item)['open']:
            items_no = len(childrens(first_item))
            parent = first_item
        
        else:
            parent = ''

        last_item = childrens(parent)[items_no - 1]
        
        wdgt.selection_set(last_item)
        wdgt.focus(last_item)
        wdgt.see(last_item)

    #~ Tables ----------------------------------------------------------
    def select_table_prev_item(self, *event):
        table = self.parent.tablelist
        sel_item = table.selection()
        filenav = self.parent.filenav

        if not table.prev(sel_item):
            first_item = table.get_children()[0]
            norm_unit = filenav.norm_scroll_unit
            dn_sldr_pos = (int(first_item) - 2) * norm_unit
            filenav.table_scroll_handler('moveto', dn_sldr_pos)
            
            first_item = table.get_children()[0]
            table.selection_set(first_item)
        else:
            prev_item = table.prev(sel_item)
            table.selection_set(prev_item)
            
        self.update_navigator_chooser_value(table.selection()[0])
    
    def moveto_table_prev_page(self, event):
        table = self.parent.tablelist
        filenav = self.parent.filenav
        
        up_sldr_pos = filenav.tablescroll.get()[0] - filenav.norm_visible_row_limit

        if up_sldr_pos >= 0:
            filenav.table_scroll_handler('moveto', up_sldr_pos)
        else:
            filenav.table_scroll_handler('moveto', 0)
        
        #~ TODO: Maintain items selection
            
    def moveto_table_first_item(self, *event):
        self.parent.filenav.table_scroll_handler('moveto', 0)
            
    def select_table_first_item(self, *event):
        table = self.parent.tablelist
        self.moveto_table_first_item()
        table.selection_set(1)
        self.update_navigator_chooser_value(1)
    
    def select_table_next_item(self, *event):
        table = self.parent.tablelist
        sel_item = table.selection()
        filenav = self.parent.filenav
        
        if not table.next(sel_item):
            first_item = table.get_children()[0]
            norm_unit = filenav.norm_scroll_unit
            dn_sldr_pos = int(first_item) * norm_unit
            filenav.table_scroll_handler('moveto', dn_sldr_pos)
            last_item = table.get_children()[-1]
            table.selection_set(last_item)
        else:
            next_item = table.next(sel_item)
            table.selection_set(next_item)
            
        self.update_navigator_chooser_value(table.selection()[0])
        
    def moveto_table_next_page(self, event):
        filenav = self.parent.filenav
        dn_sldr_pos = filenav.tablescroll.get()[1]
        if dn_sldr_pos < 1:
            filenav.table_scroll_handler('moveto', dn_sldr_pos)
        #~ TODO: Maintain items selection

    def moveto_table_last_item(self, *event):
        self.parent.filenav.table_scroll_handler('moveto', 1)
    
    def select_table_last_item(self, *event):
        table = self.parent.tablelist
        self.moveto_table_last_item()
        last_item = table.get_children()[-1]
        table.selection_set(last_item)
        #~ self.select_table_items()
        self.update_navigator_chooser_value(table.selection()[0])
        
    def focus_table_navigator(self, event):
        self.parent.table_navigator_entry.focus()
        
    def focus_table_step(self, event):
        self.parent.table_step_entry.focus()
        
    def unfocus_table_navigator_reset(self, event):
        self.update_navigator_chooser_value('')
        self.reset_step_value()
        #~ self.parent.prev_rec_btn['state'] = 'disabled'
        #~ self.parent.next_rec_btn['state'] = 'disabled'

    def update_navigator_chooser_value(self, record):
        navigator_chooser = self.parent.table_navigator_entry
        navigator_chooser.delete(0, 'end')
        navigator_chooser.insert('end', record)

    def reset_step_value(self):
        step_entry = self.parent.table_step_entry
        step_entry.delete(0, 'end')
        step_entry.insert('end', 1)
    
    def confirm_step_value(self, event):
        self.get_step_value()
        self.parent.tablelist.focus_set()

    def get_navigator_value(self):
        table = self.parent.tablelist
        
        try:
            value = int(self.parent.table_navigator_entry.get())
        except ValueError:
            # TODO: Log message
            self.update_navigator_chooser_value(1)
            value = 0
            
        feats_no = self.parent.filenav.featsno
        
        if type(value) != int or value < 1 or value > feats_no:
            value = 0
            try:
                self.update_navigator_chooser_value(table.selection()[0])
            except:
                # TODO: Log message
                self.update_navigator_chooser_value(1)
                
        return value
        
    def get_step_value(self, *event):
        try:
            step = int(self.parent.table_step_entry.get())
        except ValueError:
            # TODO: Log message
            step = 1

        feats_no = self.parent.filenav.featsno
        if type(step) != int or step < 1 or step > (feats_no - 1):
            step = 1

        self.parent.table_step_entry.delete(0, 'end')
        self.parent.table_step_entry.insert('end', step)

        return step
        
    def do_prev_step(self, *event):
        step = self.get_step_value()
        if step == 1:
            self.select_table_prev_item()
        else:
            table = self.parent.tablelist
            try:
                item = table.selection()[0]
            except:
                item = 1
                
            prev_item = int(item) - step
            if prev_item > 0:
                self.select_table_x_item(prev_item)

    def do_next_step(self, *event):
        step = self.get_step_value()
        table = self.parent.tablelist
        if step == 1:
            table.focus('')
            self.select_table_next_item()
        else:
            try:
                item = table.selection()[0]
            except:
                item = 1

            featsno = self.parent.filenav.featsno
            next_item = int(item) + step
            if next_item <= featsno:
                self.select_table_x_item(next_item)
                
    def go_to_table_item(self, *event):
        item = self.get_navigator_value()
        if item != 0:
            self.select_table_x_item(item)
            self.parent.tablelist.focus_set()
        
    def select_table_x_item(self, x_item):
        filenav = self.parent.filenav
        norm_unit = filenav.norm_scroll_unit
        table = self.parent.tablelist
        
        try:
            table.selection_set(x_item)
            table.focus(x_item)
        except:
            x_sldr_pos = int(x_item - 1) * norm_unit
            filenav.table_scroll_handler('moveto', x_sldr_pos)
            table.selection_set(x_item)
    
        #~ self.select_table_items()
        
    def select_table_items(self, *event):
        #~ if self.parent.prev_rec_btn['state'] == 'disabled':
            #~ self.parent.prev_rec_btn['state'] = 'normal'
            #~ self.parent.next_rec_btn['state'] = 'normal'

        table = self.parent.tablelist
        selection = table.selection()[0]
        self.update_navigator_chooser_value(selection)
        
        #~ TODO: Store real-table selected items list
        #~ table = self.parent.tablelist
        #~ selected_iids = [] # "item(s) selected"
        #~ print table.selection()
        #~ selected_iids.append(table.selection())
        #~ print selected_iids
        #~ self.selected_iids = selected_iids
        
    def select_table_column(self, tree, column):
        pass
        #~ TODO:
        #~ get column id -> shp.get field id -> shp.get record[id] list
        #~ styling that column only ??
        #~ add popupmenu or activate exports button (table toolbox)
        
    def active_table_item(self, event):
        pass
        #~ TODO: add action (view(record table view ~NavTable)/edit record...)
    
    def get_list_range(self, event):
                   #~ (self, treeview)
        #~ TODO: self.first/last_item
        wdgt = event.widget
        hgt1 = wdgt.winfo_y()
        hgt2 = wdgt.winfo_height()
        first_item = wdgt.identify_row(hgt1)
        last_item = wdgt.identify_row(hgt2)
        
    def toggle_selection(self, event=None):
        if event:
            wdgt = event.widget
        
        else:
            wdgt = self.parent.filelist
            
        sel_items = wdgt.selection()
        self.select_all_items(event)
        wdgt.selection_toggle(sel_items)
    
    def toggle_tab(self, nb, tab):
        nb.tab(tab, state='normal')
        nb.select(tab)
        
    def set_tab_state(self, nb, tab_state, *tabs):
        for tab_id in tabs:
            nb.tab(tab_id, state=tab_state)

    def select_tree_tab(self, event):
        wdg = event.widget
        if wdg.select() == wdg.tabs()[1]:
            tree = self.parent.filetree
            first = tree.get_children()[0]
            tree.selection_set(first)
            
    def select_content_tab(self, event):
        wdg = event.widget
        if wdg.select() == wdg.tabs()[3]:
            self.get_preview_focus()
    
    def open_directory(self, homedir=False):
        initialdir = self.parent.default_homedir
        directory = filedialog.askdirectory(initialdir=initialdir)

        #~ TODO: on cancel -> message
        if homedir:
            msg_text = _("Directory opened:")
            msg = "%s %s" % (msg_text, homedir)
            logging.info(msg)
            self.parent.add_status_text(msg)
            self.parent.set_default_homedir(directory)
            self.parent.filenav.populate_bookmarks_tree()
        
        if directory:
            msg_text = _("Changed directory to:")
            msg = "%s %s" % (msg_text, directory)
            logging.info(msg)
            self.parent.add_status_text(msg)
            self.change_rootdir(directory)

    def set_as_session_homedir(self, *event):
        current_dir = self.parent.current_dir
        self.parent.set_default_homedir(current_dir)
        self.parent.filenav.populate_bookmarks_tree()

    def set_as_default_homedir(self, *event):
        current_dir = self.parent.current_dir
        self.parent.set_default_homedir(current_dir)
        self.parent.configs.set("general", "default_homedir",
                                current_dir)
        self.update_preferences()
        self.parent.filenav.populate_bookmarks_tree()
            
    def show_preferences(self):
        prefs_win = tk.Toplevel(self.parent)
        prefs_win.wm_title(_("Preferences"))
        bg_color = self.parent.childwins_bg
        fg_color = self.parent.childwins_fg
        prefs_win.configure(background=bg_color)
        prefs_win.resizable(0, 0)
        
        self.lang_change = False
        self.prefs_win = prefs_win
        
        #~ --wrapper
        #~ --content
        
        gprefs = ttk.LabelFrame(prefs_win, text=_("General"))
        gprefs.pack(fill='x', expand=1, padx=10, pady=10)
        
        #~ General preferences ----
        
        #~ Language:
        label_text = _("Language:")
        language_label = ttk.Label(gprefs, text=label_text)
        language_label.grid(row=1, sticky='w', padx=5, pady=5)

        self.languages = {'en': _("English"), 'es': _("Spanish"),
                          'gal':_("Galician")}
                          #~ 'pt':_("Portuguese"), 'it':_("Italian")}
        lang_text = self.languages[self.parent.default_language]
        
        self.languagevar = tk.StringVar()
        self.languagevar.set(lang_text)
        language_cb = ttk.Combobox(gprefs, textvariable=self.languagevar)
        language_cb.grid(row=1, column=3, sticky='e', padx=5, pady=5)
        language_cb['values'] = self.languages.values()

        language_cb.bind('<<ComboboxSelected>>', self.set_language_change)
        
        #~ Default homedir:
        defhomedir_label = ttk.Label(gprefs,
                                     text=_("Default home directory:"))
        defhomedir_label.grid(row=2, sticky='w', padx=5, pady=5)
        
        defhomedir = tk.StringVar()
        defhomedir_entry = ttk.Entry(gprefs, textvariable=defhomedir)
        self.defhomedir_entry = defhomedir_entry
        defhomedir_entry.grid(row=2, columnspan=2, column=2, padx=5, pady=5)
        directory = self.parent.config_default_homedir
        defhomedir_entry.insert('end', directory)
        #~ FIX: Setting by entry without filedialog
        btn_path = ttk.Button(gprefs,
                                  image=self.parent.iconopendir,
                                  command=self.set_pref_default_homedir)
                                  
        btn_path.grid(row=2, column=4, padx=5)
        
        #~ History records limit:
        label_text = _("History records limit (x back, x forward):")
        histlimit_label = ttk.Label(gprefs, text=label_text)
        histlimit_label.grid(row=3, sticky='w', padx=5, pady=5)

        self.histlimit = tk.IntVar()
        self.histlimit.set(self.parent.default_history_limit)
        histlimit_spin = tk.Spinbox(gprefs, from_=1, to=30,
                                    textvariable=self.histlimit,
                                    command=self.set_pref_history_limit)
        histlimit_spin.configure(background=bg_color, foreground=fg_color)
        histlimit_spin.grid(row=3, column=3, padx=5, pady=5)
        histlimit_spin.bind('<FocusOut>',
                            lambda x: self.set_pref_history_limit)
        
        #~ Double extensions:
        label_text = _("Double extensions:")
        doublexts_label = ttk.Label(gprefs, text=label_text)
        doublexts_label.grid(row=4, sticky='w', padx=5, pady=5)

        #~ FIX: doublexts entry
        doublextsvar = tk.StringVar()
        doublextsvar.set(self.parent.default_doubleexts)
        doublexts_entry = ttk.Entry(gprefs, textvariable=doublextsvar)
        doublexts_entry.grid(row=4, columnspan=2, column=2, padx=5, pady=5)
        doublexts_entry.bind('<FocusOut>',
                             lambda x: self.set_preference('general',
                                                           'doubleexts',
                                                            doublextsvar.get()))

        #~ Shapefile preferences -------
        shpprefs = ttk.LabelFrame(prefs_win, text=_("Shapefiles"))
        shpprefs.pack(fill='x', expand=1, padx=10, pady=10)
        
        #~ Shapefile extensions:
        label_text = _("Shapefile extensions:")
        shpexts_label = ttk.Label(shpprefs, text=label_text)
        shpexts_label.grid(row=1, sticky='w', padx=5, pady=5)
        
        shpextsvar = tk.StringVar()
        shpextsvar.set(self.parent.default_shpexts)
        shpexts_entry = ttk.Entry(shpprefs, textvariable=shpextsvar)
        shpexts_entry.grid(row=1, columnspan=2, column=2, padx=5, pady=5)
        shpexts_entry.bind('<FocusOut>', 
                           lambda x: self.set_preference('shape',
                                                         'shpexts',
                                                         shpextsvar.get()))
                           
        #~ Shapefile encoding:
        label_text = _("Default shape encoding:")
        encoding_label = ttk.Label(shpprefs, text=label_text)
        encoding_label.grid(row=3, sticky='w', padx=5, pady=5)
        
        encodingvar = tk.StringVar()
        encodingvar.set(self.parent.shp_encoding)
        encoding_cb = ttk.Combobox(shpprefs, textvariable=encodingvar)
        encoding_cb.grid(row=3, column=3, sticky='e', padx=5, pady=5)
        encoding_cb['values'] = ('iso-8859-1', 'utf8', 'utf16')
        encoding_cb.bind('<<ComboboxSelected>>',
                         lambda x: self.set_preference('shape',
                                                       'shp_encoding',
                                                       encodingvar.get()))
        
        #~ Shapemode by default:
        self.shpmodevar = tk.BooleanVar()
        self.shpmodevar.set(self.parent.default_shapemode)
        shpmode_cb = ttk.Checkbutton(shpprefs,
                                     text=_("Shape mode by default"),
                                     variable=self.shpmodevar,
                                     command=self.set_pref_shapemode)
        shpmode_cb.grid(row=4, sticky='w', padx=5, pady=5)

        #~ Apply-Cancel Buttons
        buttons = ttk.Frame(prefs_win)
        buttons.pack(padx=10, pady=10)
        button_c = ttk.Button(buttons, text=_("Cancel"),
                                command=prefs_win.destroy)
        button_c.grid(row=0, column=0)
        
        button_a = ttk.Button(buttons, text=_("Apply"),
                                  command=self.apply_preferences)
        button_a.grid(row=0, column=1)
        
        def apply_focus(event=None):
            button_a.focus()
        button_a.bind('<Enter>', apply_focus)

        #~ TODO: Change Close callback -> destroy
        
        #~ --content
        #~ --wrapper

        prefs_win.focus_set()
        prefs_win.transient(self.parent)        
        prefs_win.grab_set()
        self.parent.center_window(prefs_win)
        self.parent.wait_window(prefs_win)
        
    def set_language_change(self, event):
        self.lang_change = True
        
    def set_pref_language(self):
        lang_text = self.languagevar.get()
        langs = self.languages
        lang_code = langs.keys()[langs.values().index(lang_text)]
        self.parent.configs.set("general", "default_lang", lang_code)
        self.parent.set_language(lang_code)
        
    def set_pref_default_homedir(self):
        initialdir = self.parent.default_homedir
        
        try:
            os.listdir(initialdir)
        except:
            initialdir = os.environ['HOME']
        
        directory = filedialog.askdirectory(initialdir=initialdir,
                                            parent=self.prefs_win)
        
        if directory:
            self.parent.configs.set("general", "default_homedir",
                                    directory)
            self.defhomedir_entry.delete(0, 'end')
            self.defhomedir_entry.insert('end', directory)

    def set_pref_history_limit(self):
        self.parent.configs.set("general", "history_limit", self.histlimit.get())
    
    def set_pref_shapemode(self):
        self.parent.configs.set("shape", "shapemode", self.shpmodevar.get())
    
    def set_preference(self, config_section, config_pref, get_var):
        self.parent.configs.set(config_section, config_pref, get_var)
    
    def update_preferences(self):
        ship_path = self.parent.ship_path
        conf_file = '%s/%s' % (ship_path, 'ship.conf')
        with open(conf_file, 'wb') as configfile:
            self.parent.configs.write(configfile)
        self.parent.get_default_confs()
    
    def apply_preferences(self):
        if self.lang_change:
            self.set_pref_language()
            
        self.prefs_win.destroy()
        self.update_preferences()
        
    #~ -----------------------------------------------------------------
        
    def tree_focus(self, tree, nb=1, tab=1):
        if nb == 1:
            nb = self.parent.n1
        
        elif nb == 2:
            nb = self.parent.n2
            
        self.toggle_tab(nb, tab)
        
        #~ ???: (shape to list:no content), shp_err to table:no content
        try:
            node = tree.selection()[0]
        
        except IndexError:
            try:
                node = tree.get_children()[0]
        
            except IndexError:
                node = tree.selection()[0]
        
        tree.selection_set(node)
        tree.focus_set()
        tree.focus(node)
        
    def get_tree_focus(self, *event):
        self.tree_focus(self.parent.filetree)
        
    def get_bookmarks_focus(self, *event):
        self.tree_focus(self.parent.bookmarks, tab=0)
    
    def get_ddbbs_focus(self, *event):
        self.tree_focus(self.parent.tooltree, tab=2)
        
    def get_tools_focus(self, *event):
        self.tree_focus(self.parent.tooltree, tab=3)

    def get_filelist_path_entry_focus(self, *event):
        self.parent.filelist_path_entry.select_range(0, 'end')

    #~ -----------------------------------------------------------------
    #~ -----------------------------------------------------------------

    def get_list_focus(self, *event):
        self.tree_focus(self.parent.filelist, nb=2, tab=0)

    def get_filelist_focus(self, *event):
        '''
        TODO: if shape -> table focus
              if directory -> content focus
              nb tabs depends on content tab state hidden/shown
              (content)|table tab id could be 0/1
        '''
        pass
    
    def get_table_focus(self, *event):
        tree_sel_item = self.parent.filetree.selection()
        tree_item = self.parent.filetree.item(tree_sel_item)
        #~ list_sel_item = self.parent.filelist.selection()
        #~ list_item = self.parent.filetree.item(tree_sel_item)
        
        #~ type = shape? -> only focus table if item type is shape
        #~ TODO: or if shp_err, type shp.zip
        if tree_item['values'][1] == "shape" \
        or tree_item['values'][1] == "sqliteshp":
            self.tree_focus(self.parent.tablelist, nb=2, tab=1)

    def get_table_focus2(self, *event):
        tree_item = self.get_selected_filetree_file()
        shpfile = tree_item['values'][0]
        self.parent.filenav.populate_table(shpfile)
        self.parent.n2.select(1)
            
    def show_shape_table(self, *event):
        tree_sel_item = self.parent.filetree.selection()
        tree_item = self.parent.filetree.item(tree_sel_item)
        shpfile = tree_item['values'][0]
        self.parent.filenav.populate_table(shpfile)
        self.tree_focus(self.parent.tablelist, nb=2, tab=1)

    #~ -----------------------------------------------------------------
    #~ -----------------------------------------------------------------
    
    '''
    TODO: if focus ocurs when filelist shp selected, focus filetree in
          shp
          or... use action: self.filelist.bind('<<TreeviewOpen>>') to
          focus on shapefile in filetree and don't show tabs
          table|info|preview, just content
    '''
    
    def get_selected_filetree_file(self):
        tree = self.parent.filetree
        tree_sel_item = tree.selection()
        tree_item = tree.item(tree_sel_item)
        return tree_item
        
    def get_infotab_focus2(self, *event):
        tree_item = self.get_selected_filetree_file()
        item_type = tree_item['values'][1]
        valid_item_type = ["shape", "shpzip", "sqliteshp", "sqlitezip",
                           "shapeezy"]
        if item_type in valid_item_type:
            geofile = tree_item['values'][0]
            self.parent.n2.select(2)
            self.parent.filenav.populate_infotab(geofile, item_type)
        
    def get_preview_focus2(self, *event):
        self.parent.n2.select(3)


    def get_infotab_focus(self, *event):
        if self.parent.focus_get() == self.parent.filelist:
            tree = self.parent.filelist
            sel_item = tree.focus()
        else:
            tree = self.parent.filetree
            sel_item = tree.selection()[0]
            
        item_type = tree.item(sel_item)['values'][1]
        valid_item_type = ["shape", "shpzip", "sqliteshp", "sqlitezip",
                           "shapeezy"]
        if item_type in valid_item_type:
            geofile = tree.item(sel_item)['values'][0]
            self.parent.n2.select(2)
            self.parent.filenav.populate_infotab(geofile, item_type)
        
    def get_preview_focus(self, *event):
        focus = self.parent.focus_get()
        if focus == self.parent.filelist \
        or focus == self.parent.n2:
            tree = self.parent.filelist
            sel_item = tree.focus()
        else:
            tree = self.parent.filetree
            sel_item = tree.selection()[0]
            
        item_type = tree.item(sel_item)['values'][1]
        preview_types = ["shape", "shpzip", "sqliteshp"]
        if item_type in preview_types:
            geofile = tree.item(sel_item)['values'][0]
            self.parent.n2.select(3)
            self.parent.filenav.draw_preview(geofile)

    def get_projinfotab_focus(self, *event):
        if self.parent.focus_get() == self.parent.filelist:
            tree = self.parent.filelist
            sel_item = tree.focus()
        else:
            tree = self.parent.filetree
            sel_item = tree.selection()[0]
            
        #~ item_type = tree.item(sel_item)['values'][1]
        #~ valid_item_type = ["shape", "shpzip", "sqliteshp", "sqlitezip"]
        #~ if item_type in valid_item_type:
        geoprojfile = tree.item(sel_item)['values'][0]
        self.parent.n2.select(4)
        self.parent.filenav.populate_projinfotab(geoprojfile)

    #~ -----------------------------------------------------------------
    #~ -----------------------------------------------------------------

    def toggle_panel(self, panel):
        pass
        '''
        TODO: This unique method to toggle main, tree and log/console
              panels.
        '''
    def toggle_menubar(self, event):
        parent = self.parent
        win_size = parent.winfo_geometry()
        
        if self.parent.cget('menu') == '':
            parent.config(menu=parent.menubar)
            parent.main_statusbar_label.set(_("Toggle Menu: F7, Menu navigation: F10"))
        else:
            parent.config(menu='')
            parent.main_statusbar_label.set(_("Toggle Menu: F7"))

        #~ if fullscreen, needed to resize window in order to make
        #~ menu visible again
        parent.geometry(win_size)
            
    def toggle_toolbar(self, *event):
        mp = self.parent.main_panel

        if str(self.parent.toolbar_panel) in mp.panes():
            mp.remove(self.parent.toolbar_panel)
        else:
            mp.remove(self.parent.main_windowp)
            mp.add(self.parent.toolbar_panel)
            mp.add(self.parent.main_windowp)

    def toggle_left_panel(self, *event):
        tp = self.parent.treeviews_panel
        
        if str(self.parent.lp) in tp.panes():
            tp.remove(self.parent.lp)
        
        else:
            tp.remove(self.parent.rp)
            tp.add(self.parent.lp)
            tp.add(self.parent.rp)

        if self.parent.n2.select() == self.parent.n2.tabs()[0]:
            self.get_list_focus()
        
        else:
            self.get_table_focus()
    
    def toggle_shape_mode(self):
        parent = self.parent
        
        if parent.shapemode == True:
            parent.shapemode = False
        
        elif parent.shapemode == False:
            parent.shapemode = True
       
        self.tree_focus(parent.filetree)
        
        #~ FIX: Focus
        #~ if active_widget = filelist:
            #~ self.parent.filelist.update()
            #~ self.get_list_focus()

    def change_rootdir(self, directory):
        self.parent.filenav.set_tree_root(self.parent.filetree,
                                          directory)
        self.parent.filenav.populate_list('root')

    def go_parent(self, keycomb=False):
        filetree = self.parent.filetree
        tree_sel = filetree.selection()
        index = filetree.index(tree_sel)
        
        if keycomb and index != 0:
            '''
            This is a shortcut to fix that the first element in
            childlist goes to parent-parent (just happens with key
            combination Alt+Up not with menu options). It seems to be a 
            selection problem, as if a previous tree built-in Up 
            behaviour event occurs when pressing Alt-Up.
            '''
            filetree.event_generate('<Down>')
            tree_sel = filetree.selection()
        
        tree_parent_dir = filetree.parent(tree_sel)

        if not tree_parent_dir:
            cur_path = self.parent.filetree.item(tree_sel)['values'][0]
            parent_dir = os.path.dirname(cur_path)
            self.change_rootdir(parent_dir)
            
        else:
            filetree.selection_set(tree_parent_dir)
            filetree.focus(tree_parent_dir)
            filetree.see(tree_parent_dir)
            self.get_tree_focus()
    
    #~ TODO: ? Go to parents, not dir itself
    #~ FIX: ? disable back,forward buttons when hist lists become empty
    def go_back(self):
        cur_dir = self.parent.backdirs.pop()
        
        try:
            back_dir = self.parent.backdirs.pop()
        
        # pop from empty list exception:
        except IndexError:
            self.parent.backdirs.append(cur_dir)
            #~ TODO: Add message to status bar
            msg = _("Previous directory not available")
            logging.warning(msg)
            self.parent.add_status_text(msg)
            return

        self.change_rootdir(back_dir)
        #~ TODO: ? List focus
        
        if not self.parent.frwddirs \
        or self.parent.frwddirs[-1] != cur_dir:
            self.parent.frwddirs.append(cur_dir)
            lim = self.parent.history_limit
            self.parent.frwddirs = self.parent.frwddirs[-lim:]
        
    def go_frwd(self):
        try:
            frwd_dir = self.parent.frwddirs.pop()
        
        # pop from empty list exception:
        except IndexError:
            #~ TODO: Add message to status bar
            msg = _("Next directory not available")
            logging.warning(msg)
            self.parent.add_status_text(msg)
            return

        self.change_rootdir(frwd_dir)
        
    def go_default_home(self):
        self.change_rootdir(self.parent.default_homedir)
        
    def add_bookmark(self, *event):
        directory = self.parent.current_dir
        bkmrk_name = os.path.basename(directory)
        bookmarks = self.parent.default_bookmarks
        
        if bookmarks.has_key(bkmrk_name):
            timestamp = int(time.time())
            bkmrk_name += '_%s' % (str(timestamp))
        
        #~ FIX: exception -> not allowed characters to set configs
        bookmarks[bkmrk_name] = [bkmrk_name, directory]
        self.update_bookmarks()
        
        self.parent.filenav.populate_bookmarks_tree()
                
        msg_text = _("Added bookmark")
        msg_text_2 = _("pointing to")
        msg = '%s "%s" %s %s' % (msg_text, bkmrk_name, msg_text_2,
                                 directory)
        logging.info(msg)
        self.parent.add_status_text(msg)

    def add_edit_bookmark(self):
        self.set_new_bookmark_path(new=True)
    
    def delete_bookmark(self):
        tree = self.bkmrks_list_tree
        sel_item = tree.focus()
        bookmarks = self.parent.default_bookmarks
        
        bkmrk_id = tree.item(sel_item)['values'][1]
        bookmarks.pop(bkmrk_id)
        
        self.update_edit_bookmarks()
        
    def read_bookmark_info(self, event):
        tree = event.widget
        sel_item = tree.focus()
        if sel_item == '':
            sel_item = tree.get_children()[0]
            
        bkmrk_id = tree.item(sel_item)['values'][1]
        bookmarks = self.parent.default_bookmarks
        
        self.bkmrk_name_entry.delete(0, 'end')
        self.bkmrk_name_entry.insert('end', bookmarks[bkmrk_id][0])
        self.bkmrk_path_entry.delete(0, 'end')
        self.bkmrk_path_entry.insert('end', bookmarks[bkmrk_id][1])
        
    def update_bookmarks(self, bkmrk_group='bookmarks'):
        config_file = self.parent.configs
        bookmarks = self.parent.default_bookmarks
        
        config_file.remove_section(bkmrk_group)
        config_file.add_section(bkmrk_group)
        
        for bookmark in bookmarks.keys():
            bkmrk_name = bookmarks[bookmark][0]
            bkmrk_path = bookmarks[bookmark][1]
            bkmrk_info_str = '%s;%s' % (bkmrk_name, bkmrk_path)
            config_file.set("bookmarks", bkmrk_name, bkmrk_info_str)
            
        self.update_preferences()
        
    def update_edit_bookmarks(self):
        self.update_bookmarks()
        
        tree = self.bkmrks_list_tree
        bookmarks = self.parent.default_bookmarks
        
        self.parent.filenav.populate_bookmarks_tree()
        tree.delete(*tree.get_children())
        self.parent.filenav.populate_bookmarks(tree, bookmarks, '')
        first = tree.get_children()[1]
        tree.focus_set()
        tree.focus(first)
        tree.selection_set(first)
        tree.see(first)
        
    def edit_bookmark_option(self):
        tree = self.bkmrks_list_tree
        sel_item = tree.focus()
        if sel_item == '':
            sel_item = tree.get_children()[0]
            
        bkmrk_id = tree.item(sel_item)['values'][1]
        bookmarks = self.parent.default_bookmarks
        
        bkmrk_name = bookmarks[bkmrk_id][0]
        bkmrk_path = bookmarks[bkmrk_id][1]
        
        bkmrk_name = self.bkmrk_name_entry.get()
        bkmrk_path = self.bkmrk_path_entry.get()

        bookmarks[bkmrk_id] = [bkmrk_name, bkmrk_path]
        self.update_edit_bookmarks()

    def set_new_bookmark_path(self, new=False):
        path_entry = self.bkmrk_path_entry
        name_entry = self.bkmrk_name_entry
        directory = filedialog.askdirectory(initialdir=path_entry.get(),
                                            parent=self.bkmrks_edit_win)
        if directory:
            path_entry.delete(0, 'end')
            path_entry.insert('end', directory)
            nu_name = "--%s" % (os.path.basename(directory))
            if new == True:
                name_entry.delete(0, 'end')
                nu_name = "%s" % (os.path.basename(directory))
                
            name_entry.insert('end', nu_name)
            name_entry.select_range(0, 'end')
        
    def edit_bookmarks(self, *event):
        bkmrks_edit_win = tk.Toplevel(self.parent)
        bkmrks_edit_win.wm_title(_("Edit bookmarks"))
        bg_color = self.parent.childwins_bg
        fg_color = self.parent.childwins_fg
        bkmrks_edit_win.configure(background=bg_color)
        bkmrks_edit_win.resizable(0, 0)
        self.bkmrks_edit_win = bkmrks_edit_win
        
        bkmrks_list = ttk.Frame(bkmrks_edit_win)
        bkmrks_entries = ttk.Frame(bkmrks_edit_win)
        bkmrks_buttons = ttk.Frame(bkmrks_entries)
        bkmrks_close = ttk.Frame(bkmrks_entries)

        bkmrks_list.grid(row=0, column=0)
        bkmrks_entries.grid(row=0, column=1, padx=20)

        bkmrks_list_tree = ttk.Treeview(bkmrks_list, selectmode="browse",
                                        style="Ftree.Treeview")
        bkmrks_list_tree.heading('#0', text='Bookmarks')
        bkmrks_list_tree.grid(padx=10, pady=10)
        self.bkmrks_list_tree = bkmrks_list_tree
        
        bookmarks = self.parent.default_bookmarks
        self.parent.filenav.populate_bookmarks(bkmrks_list_tree,
                                               bookmarks, '')
        
        #~ Bookmarks edit entries
        bkmrk_name_label = ttk.Label(bkmrks_entries, text=_("Name:"))
        bkmrk_name_label.grid(row=0, column=0, pady=5, sticky='w')
        
        bkmrk_name = tk.StringVar()
        bkmrk_name_entry = ttk.Entry(bkmrks_entries, width=40,
                                     textvariable=bkmrk_name)
        bkmrk_name_entry.grid(row=1, column=0)
        self.bkmrk_name_entry = bkmrk_name_entry
        
        bkmrk_path_label = ttk.Label(bkmrks_entries, text=_("Path:"))
        bkmrk_path_label.grid(row=2, column=0, pady=5, sticky='w')
        
        bkmrk_path = tk.StringVar()
        bkmrk_path_entry = ttk.Entry(bkmrks_entries, width=40,
                                     textvariable=bkmrk_path)
        bkmrk_path_entry.grid(row=3, column=0)
        self.bkmrk_path_entry = bkmrk_path_entry
        self.bkmrk_path = bkmrk_path
        btn_path = ttk.Button(bkmrks_entries,
                              image=self.parent.iconopendir,
                              command=self.set_new_bookmark_path)
        btn_path.grid(row=3, column=1, padx=5)
        
        
        #~ Apply, Add-Delete, Close Buttons
        bkmrks_buttons.grid(row=4, column=0, padx=20)

        button_add = ttk.Button(bkmrks_buttons,
                                text=_("Add"),
                                command=self.add_edit_bookmark)
        button_add.grid(row=0, column=1)
        button_del = ttk.Button(bkmrks_buttons,
                                text=_("Delete"),
                                command=self.delete_bookmark)
        button_del.grid(row=0, column=2)
        button_apply = ttk.Button(bkmrks_buttons,
                                  text=_("Apply changes"),
                                  command=self.edit_bookmark_option)
        button_apply.grid(row=0, column=3, padx=30, pady=20)
        
        bkmrks_close.grid(row=5, column=0, sticky=tk.E)
        button_c = ttk.Button(bkmrks_close, text=_("Close"),
                              command=bkmrks_edit_win.destroy)
        button_c.grid()
        
        bkmrks_list_tree.bind('<FocusIn>', self.read_bookmark_info)
        bkmrks_list_tree.bind('<<TreeviewSelect>>', self.read_bookmark_info)

        try:
            first = bkmrks_list_tree.get_children()[0]
            bkmrks_list_tree.selection_set(first)
        except:
            msg = _("No bookmarks to retrieve")
            logging.info(msg)
        
        bkmrks_edit_win.focus_set()
        bkmrks_edit_win.transient(self.parent)        
        bkmrks_edit_win.grab_set()
        self.parent.center_window(bkmrks_edit_win)
        self.parent.wait_window(bkmrks_edit_win)
        
    def get_help_contents(self):
        #~ ???: Works in Windows?
        #~ opsys = platform_system()
        #~ if opsys == 'Windows':
        #~ else:
        ship_path = self.parent.ship_path
        local_docs_rel_path = '../docs/_build/html/user_guide.html'
        local_docs_path = '%s/%s' % (ship_path, local_docs_rel_path)
        local_docs_abs_path = os.path.abspath(local_docs_path)
        local_docs_abs_path = os.path.normpath(local_docs_abs_path)
        if os.path.exists(local_docs_abs_path):
            webbrowser_open("file://%s" % local_docs_abs_path)
        else:
            self.get_online_help_contents()
        
    def get_online_help_contents(self):
        url = "http://shipshapefilenavigator.readthedocs.org/en/latest/user_guide.html"
        webbrowser_open(url)
    
    def get_website(self):
        url = "http://www.shipshapefilenavigator.org"
        webbrowser_open(url)
        
    def show_about(self):
        about_win = tk.Toplevel(self.parent)
        about_win.wm_title(_("About"))
        bg_color = self.parent.bg_color
        about_win.configure(background=bg_color)
        about_win.resizable(0, 0)
        
        #~ FIX: Refactor: make this a general function dialogwin with
        #~      decorator 
        #~ -- wrapper 
        #~ -- window content
        
        shipicon = self.parent.shipabout
        #~ message = "Ship-Shape-File-Navigator"
        
        about = ttk.Label(about_win, image=shipicon)
        about.pack(fill="both", expand=1)

        button = ttk.Button(about_win, text=_("Close"),
                                command=about_win.destroy)
        button.pack(side='bottom', pady=10)
        button.focus_set()

        button.bind('<Return>', lambda x: about_win.destroy())
        
        #~ -- window content
        #~ -- wrapper 
        
        about_win.transient(self.parent)
        about_win.grab_set()
        self.parent.center_window(about_win)
        self.parent.wait_window(about_win)
        
    #~ TODO:
    #~ def on_resize_app_window(self, *evt):
        #~ self.tableheight_after = self.parent.winfo_height()
        #~ if self.parent.filenav.tableheight != self.tableheight_after:
            #~ print "tableheight different"
        
    def on_resize(self, event):
        self.parent.filenav.update_table()
        
    def close_app(self):
        parent = self.parent
        msg = _("Exiting Ship session")
        logging.info(msg)
        parent.add_status_text(msg)
        
        #~ Getting app window last configuration
        winconf = parent.winfo_geometry()
        parent.configs.set("general", "winconf", winconf)

        sashpos = parent.treeviews_panel.sashpos(0)
        parent.configs.set("general", "treespanelwidth", sashpos)

        #~ Getting last directory visited
        lastdir = self.parent.backdirs[-1]
        parent.configs.set("general", "last_dir", lastdir)

        self.update_preferences()
            
        #~ ???: make preference ~"remember last window"
        #~ FIX: ? ok in Windows?
        
        self.parent.destroy()


class ThreadCancelException(Exception):
    ''''''
    pass


class PreviewPlot(threading.Thread):
    ''''''
    def __init__(self, parent, geofile):
        threading.Thread.__init__(self)
        self.parent = parent
        self.geofile = geofile
        #~ self.queue = queue
        self._stop = threading.Event()
        
    def stop(self):
        self.cancel_draw_btn.destroy()
        self._stop.set()
        msg = _("Preview drawing stopped")
        logging.info(msg)
        self.parent.add_status_text(msg)
        
    def run(self):
        try:
            self.draw_geometries()
        except ThreadCancelException:
            msg = _("Preview drawing canceled")
            logging.info(msg)
            self.parent.add_status_text(msg)
            
    def draw_geometries(self):
        geofile = self.geofile
        #~ geofile = self.queue.get()
        canvas = self.parent.preview_canvas
        color = canvas.color
        label_up_l = self.parent.preview_coords_label_up_l
        label_up_r = self.parent.preview_coords_label_up_r
        label_dn_l = self.parent.preview_coords_label_dn_l
        label_dn_r = self.parent.preview_coords_label_dn_r

        canvas.delete(tk.ALL)
        self.parent.preview_statusbar_label_var.set('')

        cvmax_x = canvas.winfo_width() - 5
        cvmax_y = canvas.winfo_height() - 2
        
        #~ -------------------------------------------------------------
        #~ FIX: make unique def for populate_table and this

        if geofile.endswith(".shp"):
            geotype = 'shapefile'
        elif geofile.endswith(".zip"):
            geotype = 'shapefile_zipped'
        elif geofile.endswith(".sqlite") or geofile.endswith(".db"):
            geotype = 'sqliteshp'

        try:
            if geotype == 'shapefile':
                geofile_data = shape.ShapeReader(geofile)
            elif geotype == 'shapefile_zipped':
                #~ Thread status check:
                if self._stop.isSet():
                    raise ThreadCancelException("Preview canceled")
                
                geofile_data = self.parent.fileops.read_geozip_file(geofile)
                
            elif geotype == 'sqliteshp':
                geofile_data = shapedb.ShapedbReader(geofile)

        except Exception, e:
            #~ TODO: handle exception
            msg_text = _("Unable to read geofile.")
            msg = "%s %s" % (e, msg_text)
            logging.error(msg)
            self.parent.add_status_text(msg)
            raise

        #~ --------------
        #~ geofile_data = shape.ShapeReader(geofile)
        #~ -------------------------------------------------------------

        shapes_no = geofile_data.get_records_no()
        #~ geobbox = [min(x), min(y), max(x), max(y)]
        
        #~ ???: progress bar?, non-blocking gui to big sqlites?
        label_msg = _("Calculating bounding box...")
        self.parent.preview_statusbar_label_var.set(label_msg)
        
        try:
            geobbox = geofile_data.get_bounding_box()
        
            label_up_l.set("%s, %s" % (geobbox[0], geobbox[3]))
            label_up_r.set("%s, %s" % (geobbox[2], geobbox[3]))
            label_dn_l.set("%s, %s" % (geobbox[0], geobbox[1]))
            label_dn_r.set("%s, %s" % (geobbox[2], geobbox[1]))

            #~ geobbox_ranges = [x_range, y_range]
            geobbox_ranges = [geobbox[2] - geobbox[0],
                              geobbox[3] - geobbox[1]]
            geobbox_maxrange = min(geobbox_ranges)
            
            for georange in geobbox_ranges:
                if georange == 0:
                    georange = 10

            #~ Case of single point, ranges 0:
            try:
                x_nrmlzr = cvmax_x / geobbox_ranges[0]
            except ZeroDivisionError:
                x_nrmlzr = 1
                
            try:
                y_nrmlzr = cvmax_y / geobbox_ranges[1]
            except ZeroDivisionError:
                y_nrmlzr = 1
            #~ ----
                
            nrmlzr = min(x_nrmlzr, y_nrmlzr)

            cvgeobbox = [0, 0,
                         geobbox_ranges[0] * nrmlzr,
                         geobbox_ranges[1] * nrmlzr]
            bboxpadx = (cvmax_x - cvgeobbox[2]) / 2.
            bboxpady = (cvmax_y - cvgeobbox[3]) / 2.
        
            def draw_corners():
                corners = [(0, 20, 0, 0, 20, 0),
                           (cvgeobbox[2], 20, cvgeobbox[2], 0,
                            cvgeobbox[2] - 20, 0),
                           (cvgeobbox[2], cvgeobbox[3] - 20,
                            cvgeobbox[2], cvgeobbox[3],
                            cvgeobbox[2] - 20, cvgeobbox[3]),
                           (0, cvgeobbox[3] - 20, 0, cvgeobbox[3],
                            20, cvgeobbox[3])]
                           
                for corner in corners:
                    canvas.create_line(corner[0] + bboxpadx, corner[1] + bboxpady,
                                       corner[2] + bboxpadx, corner[3] + bboxpady,
                                       corner[4] + bboxpadx, corner[5] + bboxpady,
                                       fill='red', width=1)
            
            draw_corners()
            
        except:
            pass
            #~ TODO: define exception
            #~ msg = "Not able to calculate bounding box"
        
        s = ttk.Style()
        s.configure('cancel.TButton', background='#D60415')
        cancel_draw_btn = ttk.Button(self.parent.preview_coords_dn,
                                     text=_("Stop"), style='cancel.TButton',
                                     command=self.parent.filenav.stop_draw_preview)
        cancel_draw_btn.pack(side='bottom')
        self.cancel_draw_btn = cancel_draw_btn
        
        label_msg = _("Generating preview...")
        self.parent.preview_statusbar_label_var.set(label_msg)

        pb = self.parent.preview_pb
        pb_value = self.parent.pb_value
        pb_value.set(0)
        pb['maximum'] = shapes_no
        
        step_div = 20
        if shapes_no > step_div:
            #~ step 5%
            step = int(shapes_no / step_div)
        else:
            step = 1

        #~ Geometry type:
        geom_type = geofile_data.get_geom_type()[0]
        
        if geotype == 'shapefile' or geotype == 'shapefile_zipped':
            #~ Lines, Poligons
            # ???: Also Multipatch type (31) ?
            linpol_codes = [3, 5, 13, 15, 23, 25]
            #~ Points
            points_codes = [1, 8, 11, 18, 21, 28, 31]
        elif geotype == 'sqliteshp':
            #~ ???: Add more types to WKB
            linpol_codes = [2, 3, 5, 6, 1002, 1003, 1005, 2002, 2003, 2005]
            points_codes = [1, 4, 1001, 1004, 2001, 2004]

                
        start = time.time()
        
        width = int(cvgeobbox[2])
        height = int(cvgeobbox[3])
        resol = width * height
        shape_no_lim = int(resol / 4)
        
        if shapes_no < shape_no_lim:
            geom_cnt = 0
            for geom in geofile_data.get_iter_geoms():
                #~ Thread status check:
                if self._stop.isSet():
                    raise ThreadCancelException("Preview canceled")

                points = geom.points
                
                #~ Lines, Poligons
                if geom_type in linpol_codes:
                    parts = geom.parts

                    def draw_lines(points_range):
                        line_pts = []
                        for point in points_range:
                            #~ Thread status check:
                            if self._stop.isSet():
                                raise ThreadCancelException("Preview canceled")

                            x = ((point[0] - geobbox[0]) * nrmlzr) + bboxpadx
                            line_pts.append(x)
                            y = ((geobbox[3] - point[1]) * nrmlzr) + bboxpady
                            line_pts.append(y)

                        canvas.create_line(line_pts, fill=color)

                    if len(parts) == 1:
                        draw_lines(points)
                    else:
                        lim0 = parts.pop(0)
                        while parts:
                            lim1 = parts.pop(0)
                            draw_lines(points[lim0:lim1])
                            lim0 = lim1
                        draw_lines(points[lim1:])
                        
                #~ Points
                elif geom_type in points_codes:
                    for point in points:
                        x = ((point[0] - geobbox[0]) * nrmlzr) + bboxpadx
                        y = ((geobbox[3] - point[1]) * nrmlzr) + bboxpady
                        canvas.create_oval(x, y, x, y,
                                           outline=color)

                else:
                    msg = _("Not able to preview this geometry type")
                    logging.error(msg)
                    self.parent.add_status_text(msg)

                if geom_cnt % step == 0:
                #~ FIX: main thread updates idletasks anyway geom to geom
                    canvas.update_idletasks()
                
                geom_cnt += 1
                if geom_cnt % step == 0:
                    pb.step(step)
                    prct = int(geom_cnt * 100 / float(shapes_no))
                    label_text = _("shapes shown")
                    label_msg = " %s/%s (%s%%) %s " % (geom_cnt, shapes_no,
                                                       prct, label_text)
                    self.parent.preview_statusbar_label_var.set(label_msg)
                
            pb_value.set(0)

        else:
            matrx = {}
            gap = 2
            bboxpadx = int(bboxpadx)
            bboxpady = int(bboxpady)
            
            label_text = _("reading geometries...")
            label_msg = " %s (%s) " % (label_text, shapes_no)
            self.parent.preview_statusbar_label_var.set(label_msg)

            geom_cnt = 0
            for geom in geofile_data.get_iter_geoms():
                #~ Thread status check:
                if self._stop.isSet():
                    raise ThreadCancelException("Preview canceled")
                
                point = geom.points[0]
                x = int((((point[0] - geobbox[0]) * nrmlzr) / gap )) 
                y = int((((geobbox[3] - point[1]) * nrmlzr) / gap ))
                x, y = x*gap + bboxpadx, y*gap + bboxpady

                if y in matrx.keys():
                    pass
                else:
                    matrx[y] = [0,0] * width
                            
                matrx[y][x] = 1
                
                geom_cnt += 1
                
                if geom_cnt % step == 0:
                    pb.step(step)
            
            label_text = _("drawing geometries schema...")
            label_msg = " %s (%s) " % (label_text, shapes_no)
            self.parent.preview_statusbar_label_var.set(label_msg)

            # drawing pixel contour
            for y in matrx:
                row = matrx[y]
                
                first_px = row.index(1)
                row.reverse()
                last_px = len(row) - row.index(1)
                row.reverse()
                canvas.create_rectangle(first_px, y, first_px,
                                                    y, fill=color,
                                                    outline=color)
                canvas.create_rectangle(last_px, y, last_px,
                                                    y, fill=color,
                                                    outline=color)

            for y in matrx:
                row = matrx[y]
                x = 0
                gap_x = 0
                for pixel in row:
                    #~ Thread status check:
                    if self._stop.isSet():
                        raise ThreadCancelException("Preview canceled")
                        
                    if pixel == 1:
                        gap_x += gap
                        canvas.create_rectangle(x, y, x + gap, y + gap,
                                                fill=color, outline=color)

                    x += 1
                    
                #~ canvas.update_idletasks()
            pb_value.set(0)
            
        drawing_time = time.time() - start
        print drawing_time
        #~ ???: Give option to save preview as ps
        #~ canvas.postscript(file='preview.ps', x=0, y=0)
        
        msg_text = _("Drawing geometries time:")
        msg = "%s %s" % (msg_text, drawing_time)
        logging.info(msg)
        self.parent.add_status_text(msg)

        #~ Redrawing corners to be above geometries
        draw_corners()
        label_text = _("shapes preview")
        label_msg = " %s %s " % (shapes_no, label_text)
        self.parent.preview_statusbar_label_var.set(label_msg)
        
        cancel_draw_btn.destroy()
        
        #~ (x0, y0, x1, y1)
        #~ points: canvas.create_oval(150, 150, 153, 153, outline=color)
        #~                                        fill='black', width=2)
        #~ lines: canvas.create_line(0, 120, 120, 120, fill=color)
        #~ polygons: canvas.create_polygon(200, 200, 210, 230, 250, 260,
                                    #~ 240, 230, outline=color, fill='')


class FileNavigator():
    ''''''
    def __init__(self, parent):
        self.parent = parent
        
    def exec_filetree_item(self, event):
        tree_sel_item = self.parent.filetree.selection()
        tree_item = self.parent.filetree.item(tree_sel_item)
        if tree_item['values'][1] == "shape":
            self.parent.event.get_table_focus()
        #~ FIX: sometimes don't work -> needed ~event.stop() ?
        #~ TODO: add behaviour to sqlite and geopkg on open file
        #~ elif tree_item['values'][1] == "sqlite":
        #~ elif tree_item['values'][1] == "geopkg":
        else:
            self.update_tree(event)
        
    def exec_filelist_item(self, event):
        #~ TODO: -> method get_item_path
        wdgt = event.widget
        sel_item = wdgt.selection()
        
        if len(sel_item) == 1:
            sel_item = sel_item[0]
            itempath = self.parent.filelist.item(sel_item)['values'][0]
        
            #~ FIX: Permissions verification before executing.
            #~ if os.access("myfile", os.R_OK):
            #~ else: warn message
            
            if os.path.isdir(itempath):
                self.parent.event.change_rootdir(itempath)
                
                #~ TODO: go to tree_sel_dir children-text: filelist
                #~       selected-text ?
                #~ filetree = self.parent.filetree
                #~ tree_sel_dir = filetree.selection()
                #~ tree_child_dir = filetree.next(tree_sel_dir)
                # TODO: Make method ?
                #~      "change/select_tree_item(tree_new_dir)":
                #~ filetree.selection_set(tree_child_dir)
                #~ filetree.focus(tree_child_dir)
                #~ filetree.see(tree_child_dir)
                #~ self.parent.filelist.update()
                #~ self.parent.event.get_list_focus()
            
            elif os.path.isfile(itempath):
                #~ FIX: this not opens file, only opens file browser
                #~      ?-> feature ~"open with system file browser"
                opsys = platform_system()
                #~ os.uname -> (sysname, nodename, release, version,
                #~              machine)
                
                if opsys == 'Linux':
                    try:
                        os.system('xdg-open %s' %itempath)
                        
                    except:
                        #~ "Unknown file type"
                        raise
                        
                #~ TODO: non-UNIX platforms
                #~ elif os == win:
                    #~ os.startfile(itempath)
                #~ elif os == mac:
                    #~ open

    def fill_data_cells(self, min_row, max_row):
        table = self.parent.tablelist
        table.delete(*table.get_children())

        geofile_records = self.geofile_data.get_iter_records(min_row, max_row)
        row = min_row
        for record in geofile_records:
            #~ shapefile needed (sqlite not, default unicode UTF-8)
            def decoderow(value):
                if type(value) == str:
                    value = value.decode(self.parent.shp_encoding)
                    #~ value = unicode(value, shp_encoding)
                return value
                
            shpvalues = map(lambda x: decoderow(x), record)
            #~ sqlite:
            #~ shpvalues = record
            
            row += 1
            table.insert('', 'end', iid=row, text=str(row), values=shpvalues)
            
        table.pack(side='left', fill='both', expand=1)
    
    def update_table(self):
        tree_sel_item = self.parent.filetree.selection()
        tree_item = self.parent.filetree.item(tree_sel_item)
        geofile = tree_item['values'][0]
        self.populate_table(geofile)
    
    def populate_table(self, geofile):
        table = self.parent.tablelist
        table.delete(*table.get_children())
        
        if geofile.endswith(".shp"):
            geotype = 'shapefile'
        elif geofile.endswith(".zip"):
            if geofile[-7:-4] == 'shp':
                geotype = 'shapefile_zipped'
            else:
                geotype = 'sqlite_zipped'
                
        elif geofile.endswith(".sqlite") or geofile.endswith(".db"):
            geotype = 'sqliteshp'
        elif geofile.endswith(".shz"):
            geotype = 'shapeezy'
        elif geofile.endswith(".csv"):
            geotype = 'csv'

        #~ FIX: ? shp validation
        try:
            if geotype == 'shapefile':
                geofile_data = shape.ShapeReader(geofile)
                
            elif geotype == 'shapefile_zipped':
                geofile_data = self.parent.fileops.read_geozip_file(geofile)
                
            elif geotype == 'sqliteshp':
                geofile_data = shapedb.ShapedbReader(geofile)
                
            elif geotype == 'sqlite_zipped' \
            or geotype == 'shapeezy':
                geofile_zip = os.path.basename(geofile)
                geofile_db = os.path.splitext(geofile_zip)[0]
                if geotype == 'shapeezy':
                    geofile_db += '.sqlite'
                
                tmpdir = temp_mkdtemp()
                with zipfile(geofile, 'r') as dbzip:
                    dbzip.extract(geofile_db, tmpdir)
                    
                geofile = "%s/%s" % (tmpdir, geofile_db)
                geofile_data = shapedb.ShapedbReader(geofile)
                
                shutil.rmtree(tmpdir)
                
            elif geotype == 'csv':
                '''
                TODO: add other table types (xls, dbf[take care along
                      with shp mode]...)
                      create module tables reader, formats: csv, ...
                      data,featsno,fields
                      change variable names geofile -> ~datafile
                '''
                geofile_data = tables.CSVReader(geofile)
            
        #~ TODO: handle exception
        except Exception, e:
            msg_text = _("Unable to populate table.")
            msg = "%s %s" % (msg_text, e)
            logging.error(msg)
            self.parent.add_status_text(msg)
            raise

        self.geofile_data = geofile_data
        
        #~ TODO: Get shape unicode
        #~       (Western Europe-Spain default unicode iso-8859-1)
        #~ shp_encoding = self.parent.shp_encoding
        
        #~ Shape features ---
        featsno = geofile_data.get_records_no()
        self.featsno = featsno

        #~ Geofile field names ---
        if geotype == 'shapefile' or geotype == 'shapefile_zipped':
            fields = geofile_data.get_field_names()
            fieldsno = geofile_data.get_fields_no()
            geomtype = geofile_data.get_geom_type()[1]
            
        elif geotype == 'csv':
            fields = geofile_data.get_field_names()
            fieldsno = geofile_data.get_fields_no()
            delimiter = geofile_data.get_delimiter()
            geomtype = 'delimiter: "%s"' % delimiter
            
        elif geotype == 'sqliteshp' or geotype == 'sqlite_zipped'\
        or geotype == 'shapeezy':
            fields_info = geofile_data.get_fields_info()
            fieldsno = fields_info[0]
            fields = fields_info[1]
            geomtype = geofile_data.get_geom_type()[1]
        
        geofile_data_info = ' %s %s, %s %s (%s)' % (fieldsno,
                                                    _("fields"), featsno,
                                                    _("features"), 
                                                    geomtype)
        
        #~ Setting field names ---
        table['columns'] = fields

        #~ e = self.parent.event
        for field in fields:
            #~ FIX: ?? same width for all field headings ?
            table.column(fields.index(field), width=100,
                         stretch='False')
            table.heading(field, text=field,
                          #~ command=lambda f=field: self.parent.event.select_table_column(table, f))
                          command=lambda f=field: e.select_table_column(table, f))

        '''
        table = tablelist

        tablelist height is just the height of rows (without heading).
        With low number of rows it doesn't fill all tableframe so to
        know all space available we need to obtain indirecty by
        tableframe height:
        
        tableframe = headers 17px + tablelist + xscrollbar 15px + statusbar 18px
        -> tablelist_height = tableframe - 50 [17 - 15 - 18]
        
        
         tableframe
        ====================
        headers 17px
        --------------------
        _tablelist__________
        ---
        (rows 20px each)
        ---
        ____________________
        xscrollbar 15px
        --------------------
        statusbar 17px
        ====================
        '''
        max_table_height = self.parent.tableframe.winfo_height() - 50

        #~ Adding dummy feats to figure out visible rows range
        #~ row_range = 100
        #~ for row in range(row_range):
            #~ table.insert('', 'end', iid=row, text=str(row))
            
        lastvisrow_id = ''
        while lastvisrow_id == '':
            table.insert('', 'end', text='')
            lastvisrow_id = table.identify_row(max_table_height)
            lastvisrow = table.index(lastvisrow_id) + 1

        visible_row_limit = lastvisrow
        self.visible_row_limit = visible_row_limit
        
        #~ Adding rows range features
        if featsno < visible_row_limit:
            row_range = featsno
        else: 
            row_range = visible_row_limit

        #~ Filling table with geofile data
        self.fill_data_cells(0, row_range)

        #~ Setting virtual scroll
        self.norm_scroll_unit = 1. / featsno
        norm_visible_row_limit = visible_row_limit * self.norm_scroll_unit
        self.norm_visible_row_limit = norm_visible_row_limit
      
        self.tablescroll = self.parent.tablelist_yscroll
        self.tablescroll['command'] = self.table_scroll_handler
        self.tablescroll.set(0, norm_visible_row_limit)
        self.tablescroll.pack(side='right', fill='y')
        
        #~ Table status label ---
        self.parent.table_statusbar_label.set(geofile_data_info)
        #~ Table status label ---
        
    def table_scroll_handler(self, *e):
        evt, value = e[0], e[1]
        sldr_up, sldr_dn = self.tablescroll.get()
        if evt == 'scroll':
            sldr_up += self.norm_scroll_unit * float(value)
            sldr_dn += self.norm_scroll_unit * float(value)
                
        elif evt == 'moveto':
            sldr_up = float(value)
            sldr_dn = float(value) + self.norm_visible_row_limit

        if sldr_up < 0:
            sldr_dn = 0. + self.norm_visible_row_limit
            
        if sldr_dn > 1:
            sldr_dn = 1
            sldr_up = 1. - self.norm_visible_row_limit
            
        if sldr_up < 0:
            sldr_up = 0
            
        self.tablescroll.set(sldr_up, sldr_dn)
        from_row = int(round(sldr_up * self.featsno))
        to_row = int(round(sldr_dn * self.featsno))
        self.fill_data_cells(from_row, to_row)
        
        #~ set selection to selected_items

    def get_item_size(self, path):
        size = os.path.getsize(path)
        
        if size < 1024:
            sizestring = '%s B' % size
            
        elif size < 1048576:
            sizestring = '%s KB' % (int(size / 1024.))
            
        elif size < 1073741824:
            sizestring = '%s MB' % (int(size / 1024. / 1024.))
            
        else:
            sizestring = "(> 1GB)"
        
        return sizestring

    def populate_list(self, node, pop_path=None):
        if pop_path:
            node_type = 'directory'
            node_path = pop_path
        else:
            tree = self.parent.filetree
            node_type = tree.set(node, "type")
            #~ node_path = self.parent.filetree_path_entry.get()
            node_path = tree.set(node, "path")
        
        filelist = self.parent.filelist
        gui_evt = self.parent.event
        n2 = self.parent.n2
        
        filelist.delete(*filelist.get_children())
        
        geo_types = ['shape', 'shpzip', 'sqliteshp', 'sqlitezip',
                     'shapeezy']
        table_types = ['table']
        geo_dbs = ['sqlite', 'geopkg']
        errs_types = ['shape_err', 'shpzip_err', 'sqlite_err']
        
        if node_type in geo_types or node_type in table_types:
            gui_evt.set_tab_state(n2, 'hidden', 0, 4)
            gui_evt.set_tab_state(n2, 'normal', 2, 3)
            if node_type in table_types:
                #~ TODO: add Info to tables(csv)
                gui_evt.set_tab_state(n2, 'hidden', 2, 3)
            n2.select(1)
   
            #~ TODO: default geofile view application setting
            #~ ~self.parent.default_shape_view

            geofile = node_path
            try:
                self.populate_table(geofile)
            #~ ???: handle except ValueError: invalid literal for int() with base 10
            except Exception, e:
                raise
                logging.error(e)
                self.parent.add_status_text(e)
                err_file = '%s.err' % geofile
                with open(err_file, 'w') as errorfile:
                    #~ FIX: write log message (date, exception...)
                    errorfile.write(str(e))

                if node_type == 'shape':
                    tree.item(node, image=self.parent.iconshape)
                elif node_type == 'shpzip':
                    tree.item(node, image=self.parent.iconshpziperr)
                elif node_type == 'sqlite' \
                or node_type == 'sqliteshp':
                    tree.item(node, image=self.parent.icondatabaseerr)
                else:
                    tree.item(node, image=self.parent.iconerror)
            
                #~ gui_evt.set_tab_state(n2, 'hidden', 1, 3, 4)
                #~ n2.select(2)
                
            #~ TODO: add geofile info -> metadata, shape statistics
        
        elif node_type == 'geoproj':
            gui_evt.set_tab_state(n2, 'hidden', 0, 1, 2, 3)
            n2.select(4)
            gui_evt.get_projinfotab_focus()

        elif node_type in errs_types:
            gui_evt.set_tab_state(n2, 'hidden', 0, 1, 3, 4)
            n2.select(2)
        
        elif node_type in geo_dbs:
            gui_evt.set_tab_state(n2, 'hidden', 1, 2, 3, 4)
            n2.select(0)
            child_path = node_path
            db = shapedb.DbReader(child_path)
            tables = db.tables
            for table in tables:
                icon = self.parent.icontable
                child_type = 'sqlitetable'
                size = 0
                timestring = ''
                filelist.insert('', 'end', text=table, image=icon,
                                values=[unicode(child_path, "utf-8"),
                                        child_type, size, timestring])
        
        elif node_type == 'directory':
            gui_evt.set_tab_state(n2, 'hidden', 1, 2, 3, 4)
            n2.select(0)
            
            try:
                childslist = os.listdir(node_path)
            except Exception, e:
                logging.error(e)
                self.parent.add_status_text(e)
                return

            #~ FIX: separate folders - files
            #~ items = [folders, files]
            #~ items_no = len(childslist)
            childslist.sort(key=lambda x: x.lower())
            
            for child in childslist:
                child_path = os.path.join(node_path, child).replace('\\', '/')

                if os.path.isdir(child_path):
                    if os.path.islink(child_path):
                        child_type = "link"
                        icon = self.parent.iconfoldergo
                    else:
                        child_type = "directory"
                        icon = self.parent.iconfolder
                        
                    try:
                        size = "%s %s" % (len(os.listdir(child_path)),
                                          _("items"))
                    except Exception, e:
                        logging.error(e)
                        self.parent.add_status_text(e)

                elif os.path.isfile(child_path):
                    fops = self.parent.fileops
                    path_list, name, ext = fops.get_file_namelist(child_path)
                    child_name = path_list[1]
                    size = self.get_item_size(child_path)
                    #~ FIX: Shapefiles size only .shp -> add .dbf, shx...

                    #~ Setting file icon
                    #~ To avoid points in iconfile name
                    nameext = ext.replace(".","")
                    if nameext in self.parent.fileicons.keys():
                        icon = eval('self.parent.icon%s' %nameext)
                    else:
                        icon = self.parent.iconfile

                    #~ Setting child type and special icon cases
                    if ext in self.parent.shpexts \
                    and self.parent.shapemode:
                        exp = "%s/%s.shp" % (path_list[0], name)
                        if glob(exp):
                            child_type = "shp_files"
                            continue
                        else:
                            child_type = "file"

                    elif ext == 'shp':
                        child_type = "shape"
                        exp = "%s/%s.shp.err" % (path_list[0], name)
                        if glob(exp):
                            icon = self.parent.iconshapeerr
                            child_type = 'shp_err'
                            
                    elif ext == 'shp.zip':
                        icon = self.parent.iconshpzip
                        child_type = 'shpzip'
                        exp = "%s/%s.%s.err" % (path_list[0], name, ext)
                        if glob(exp):
                            icon = self.parent.iconshpziperr
                            child_type = 'shpzip_err'
                            
                    elif ext == 'sqlite' or ext == 'db':
                        child_type = "sqlite"
                        icon = self.parent.icondb
                        exp = "%s/%s.%s.err" % (path_list[0], name, ext)
                        if glob(exp):
                            icon = self.parent.icondatabaseerr
                            child_type = 'db_err'

                    elif ext == 'sqlite.zip' or ext == 'db.zip':
                        child_type = "sqlitezip"
                        icon = self.parent.icondbzip
                        
                    elif ext == 'shz':
                        child_type = "shapeezy"
                        icon = self.parent.iconshz
                        
                    elif ext == 'csv':
                        child_type = "csv"
                            
                    #~ Hides err files if shapemode:
                    elif ext == 'err' and self.parent.shapemode :
                        exp = "%s/%s" % (path_list[0], name)
                        if glob(exp):
                            continue
                            
                    elif ext == 'zip.err' and self.parent.shapemode :
                        exp = "%s/%s.%s" % (path_list[0], name, ext)
                        if glob(exp):
                            continue

                    else:
                        child_type = "file"
                        
                child_name = child
                
                #~ Modified date
                sec = os.path.getmtime(child_path)
                timestring = time.strftime('%Y-%m-%d %H:%M',
                                           time.localtime(sec))
                try:
                    filelist.insert('', 'end', text=child_name,
                                    image=icon,
                                    values=[unicode(child_path, "utf-8"),
                                            child_type, size, timestring])
                                            #~ treenode])
                    
                #~ FIX: exception "decoding Unicode is not supported"
                except TypeError:
                    #~ TODO: exception handling
                    raise
                    
            #~ Filelist path
            self.parent.filelist_path_entry.delete(0, 'end')
            self.parent.filelist_path_entry.insert(0, node_path)
            
            #~ Updating current dir
            self.parent.current_dir = node_path
            
            #~ History update
            self.update_history(node_path)
            
            #~ Table status label ---
            items_no = len(filelist.get_children())
            self.items_no = items_no
            content_info = " %s %s" % (items_no, _("items"))
            self.parent.content_statusbar_label.set(content_info)

        filelist.pack(side='left', fill='both', expand=1)
        
    def populate_infotab(self, geofile, geofile_type):
        parent = self.parent
        path_list, name, ext = parent.fileops.get_file_namelist(geofile)
        parent.geofile_name_var.set(' %s' % name)
        self.infotab_geofile = geofile
        self.geofile_type = geofile_type

        geofile_type_labels = {"shape": "Shapefile",
                               "shpzip": _("Shapefile zipped"),
                               "sqliteshp": _("Sqlite database"),
                               "sqlitezip": _("Sqlite database zipped"),
                               "shapeezy": _("Ship Shapeezy container format (.shz)")}
                          
        geotype_label = geofile_type_labels[geofile_type]
        parent.geofile_type_var.set('%s %s' % (_("Type:"),
                                    geotype_label))
        
        #~ TODO: err files
        
        if geofile_type == 'shape':
            for shpext in self.parent.shpexts:
                exp = '%s/%s.%s' % (path_list[0], name, shpext)
                if glob(exp):
                    ttk.Label(parent.infotab_file, textvariable=exp, 
                              anchor='nw').pack()
                    
        #~ TODO: list files contained inside shpzip and shapeezy
        elif geofile_type == 'shpzip':
            #~ geofile = os.path.splitext(geofile)[0]
            msg = _("Shapefile zipped file")
            logging.info(msg)
            self.parent.add_status_text(msg)
            
            geofile_data = self.parent.fileops.read_geozip_file(geofile)
        
        elif geofile_type == 'shapeezy':
            msg = _("Shapeezy file")
            logging.info(msg)
            self.parent.add_status_text(msg)

        #~ FIX: get srs string from zipped files shpzip and sqlitezip/shapeezy
        geofile_srs_dbs = ["sqliteshp", "sqlitezip", "shapeezy"]
        no_srs_text = _("srs info not avaliable")
                
        if geofile_type in geofile_srs_dbs:
            geofile_data = shapedb.ShapedbReader(geofile)
            try:
                srs_info = geofile_data.get_srs()
            except:
                srs_info = [no_srs_text, '']
                
            fields_desc = geofile_data.get_fields_description()
        else:
            #~ TODO: read shpzip zipped prj file
            prj_file = '%s/%s.prj' % (path_list[0], name)
            if os.path.exists(prj_file):
                with open(prj_file, 'rb') as prjfile:
                    prj_text = prjfile.readlines()
            else:
                prj_text = no_srs_text
                
            srs_info = ['(.prj file)', prj_text]
            if geofile_type == 'shape':
                geofile_data = shape.ShapeReader(geofile)
                
            fields_data_list = geofile_data.get_fields()[1:]
            fields_desc = map(lambda x: (x[0], "%s,%s,%s" % (x[1],
                                                             x[2],
                                                             x[3])),
                              fields_data_list)
            #~ TODO: define as string stype ('INTEGER') by dbf characteristics ('N,10,1')
        
        parent.geofile_srs_var.set('SRS: %s' % srs_info[0])
        parent.geofile_srsmsg_var.set(srs_info[1])
        
        #~ TODO: Add fields in table

        parent.geofile_fields_schema.delete(*parent.geofile_fields_schema.get_children())
        for field in fields_desc:
            index = fields_desc.index(field) + 1
            parent.geofile_fields_schema.insert('', 'end', iid=index, text=index,
                                                values=[field[0], field[1]])
        
        parent.geofile_fields_schema.selection_set(1)
        parent.geofile_fields_schema.focus_set()
        parent.geofile_fields_schema.focus(1)
        
        parent.geofile_fields_schema.bind('<<TreeviewSelect>>',
                                          self.draw_infotab_stats)

    def draw_infotab_stats(self, event):
        parent = self.parent
        canvas = parent.geofile_fields_stats
        color = parent.geofile_fields_stats.color
        color_fg = parent.geofile_fields_stats.color_fg
        stats_font = ('Sans', 6)

        wdgt = event.widget
        sel_item = wdgt.selection()
        field = wdgt.item(sel_item)['values'][0]
        #~ -------------------------------------------------------------
        field_index = wdgt.index(sel_item)
        geofile = self.infotab_geofile

        geofile_type = self.geofile_type
        geofile_srs_dbs = ["sqliteshp", "sqlitezip", "shapeezy"]
        if geofile_type in geofile_srs_dbs:
            geofile_data = shapedb.ShapedbReader(geofile)
        elif geofile_type == "shpzip":
            geofile_data = self.parent.fileops.read_geozip_file(geofile)
        else:
            geofile_data = shape.ShapeReader(geofile)


        #~ Setting canvas basic info ---
        canvas.delete(tk.ALL)
        #~ Field name ---
        canvas.create_text(5, 5, text=field, anchor=tk.NW,
                           fill=color_fg, font=stats_font)
        #~ -----------------------------

        values_no = geofile_data.get_records_no()
        #~ TODO: Add Progress bar/option to generate graphic to >5000 feats
        if values_no > 5000:
            desc_txt = _("Too many features, it could take some time to draw graph")
            canvas.create_text(20, 25, text=desc_txt, anchor=tk.W,
                               fill=color_fg, font=stats_font)
            draw_btn = ttk.Button(canvas, text=_("Generate graph"))
                                  #~ command=self.parent.filenav.stop_draw_preview)
            draw_btn.pack()
            cvwin = canvas.create_window(20, 40, anchor=tk.NW,
                                         window=draw_btn)
            return

        #~ start = time.time()

        values = geofile_data.get_field_values(field_index)

        def characterize_str(values):
            uniq_values = set(values)
            uniq_values_no = len(uniq_values)

            if uniq_values_no == 1:
                if values_no > 1:
                    desc_txt = "'%s' x%s: " % (values[0], values_no)
                    desc_txt += _("Same value for all features")
                else:
                    desc_txt = "Value: '%s'" % (values[0])
                    
                canvas.create_text(20, 25, text=desc_txt,
                                   anchor=tk.W, fill=color_fg,
                                   font=stats_font)
                    
            elif uniq_values_no == values_no:
                desc_txt = _("Each value is different")
                if type(values[1]) == int \
                or type(values[1]) == str \
                or type(values[1]) == unicode:
                    desc_txt += _(" (likely ID field)")
                canvas.create_text(20, 25, text=desc_txt, anchor=tk.W,
                                   fill=color_fg, font=stats_font)
            else:
            #~ if uniq_values_no > 1 and uniq_values_no < values_no:
                parent.update_idletasks()
                cvmax_y = canvas.winfo_height()
                bars_no = (cvmax_y - 65) / 9
                top = max(5, min(bars_no, uniq_values_no))
                top_values = [(0, '')] * top

                for val in uniq_values:
                    count = values.count(val)
                    if count > top_values[0][0]:
                        top_values.append((count, val))
                        top_values.sort()
                        top_values.pop(0)
                
                top_values.reverse()

                desc_txt = _("Frequency (count) and Relative Frequency(%) of the value")
                canvas.create_text(20, 25, text=desc_txt,
                           anchor=tk.W, fill=color_fg, font=stats_font)

                max_value = top_values[0][0]
                offsety = 0
                values_cnt = 0
                for value in top_values:
                    if value[0] == 0:
                        continue
                    bar_len = (float(value[0]) / max_value) * 90 + 30
                    rel_freq = 100 * value[0] / float(values_no)
                    freq_txt = "%5s (%1.1f%%)" % (value[0], rel_freq)
                    canvas.create_rectangle(20, 37 + offsety,
                                            bar_len, 41 + offsety,
                                            outline=color, fill=color)
                    canvas.create_text(120, 40 + offsety, text=freq_txt,
                               anchor=tk.W, fill=color_fg, font=stats_font)
                    
                    value_str = "'%s'" % (value[1])
                    val_color = 'red'
                    if str(value[1]) == '':
                        value_str += ' *null value'
                    elif re_match('^ *$', str(value[1])):
                        #~ value_str (has several spaces ' '):
                        value_str += ' *spaces warning'
                    else:
                        val_color = color_fg
                    
                    canvas.create_text(190, 40 + offsety, text=value_str,
                                       anchor=tk.W, fill=val_color,
                                       font=stats_font)
                               
                    offsety += 9
                    values_cnt += value[0]
                
                if values_cnt != values_no:
                    canvas.create_rectangle(20, 37 + offsety,
                                            21, 41 + offsety,
                                            outline=color, fill=color)
                    canvas.create_text(145, 40 + offsety, text='...',
                               anchor=tk.W, fill=color_fg, font=stats_font)
                    canvas.create_text(135, 52 + offsety,
                                   text="%s/%s" % (values_cnt, values_no),
                                   anchor=tk.W, fill=color_fg,
                                   font=stats_font)
                
        def characterize_num(values):
            if len(set(values)) < 5:
                characterize_str(values)
                return
            
            max_value = max(values)
            min_value = min(values)
                
            values.sort()

            #~ FIX: Calculate median using module statistics in python2.7???
            def get_median(values, values_no):
                median_pos = values_no / 2
                if values_no % 2 == 0:
                    median_value = (values[median_pos - 1] + values[median_pos]) / 2.
                else:
                    median_value = values[median_pos]
                
                return median_value                
                    
            q2_value = get_median(values, values_no)
            median_pos = values_no / 2

            values1 = values[:median_pos]
            q1_value = get_median(values1, values_no / 2)

            values3 = values[-median_pos:]
            q3_value = get_median(values3, values_no / 2)
            
            iq_range = q3_value - q1_value
            iq_fence = 1.5 * iq_range
            q3_fence = q3_value + 1.5 * iq_range
            q1_fence = q1_value - 1.5 * iq_range
            midhinge = (q1_value + q3_value) / 2.
            trimean = (q2_value + midhinge) / 2.

            try:
                value_range = max_value - min_value
                midrange = value_range / 2.
            except TypeError:
                #~ TODO: ??? strings info 
                return
            
            #~ Outliers fix
            max_outlimit = q2_value + 3 * iq_range
            min_outlimit = q2_value - 3 * iq_range
            
            cv_max_value, cv_min_value = max_value, min_value
            if max_value > max_outlimit:
                cv_max_value = max_outlimit
            
            if min_value < min_outlimit:
                cv_min_value = min_outlimit
                
            cv_value_range = cv_max_value - cv_min_value

            #~ -------------------------------------------------------------
            parent.update_idletasks()
            cvmax_x = canvas.winfo_width()
            cvmax_y = canvas.winfo_height()
            line_xpos = cvmax_x / 3
            line_ypos = cvmax_y - 30
            cv_boxrange = float(cvmax_y - 30 - 30)
            
            if value_range > 0:
                cv_factor = cv_boxrange / value_range
            else:
                cv_factor = 1
                
            q3_pos = line_ypos - ((q3_value - min_value) * cv_factor)
            q2_pos = line_ypos - ((q2_value - min_value) * cv_factor)
            q1_pos = line_ypos - ((q1_value - min_value) * cv_factor)
            q3_fence_pos = q3_pos - (iq_fence * cv_factor)
            if q3_fence_pos < 30:
                q3_fence_pos = 30
            q1_fence_pos = q1_pos + (iq_fence * cv_factor)
            if q1_fence_pos > line_ypos:
                q1_fence_pos = line_ypos
            
            #~ 3 IQR range ---
            #~ canvas.create_text(line_xpos - 15, 30, text='3IQR',
                               #~ anchor=tk.SE, fill=color_fg, font=stats_font)
            #~ canvas.create_text(line_xpos + 15, 30, text=cv_max_value,
                               #~ anchor=tk.SW, fill=color_fg, font=stats_font)
            #~ canvas.create_text(line_xpos + 15, line_ypos, text=cv_min_value,
                               #~ anchor=tk.NW, fill=color_fg, font=stats_font)
            #~ 1.5 IQR range ---
            canvas.create_line(line_xpos - 5, q3_fence_pos, 
                               line_xpos + 5, q3_fence_pos,
                               line_xpos, q3_fence_pos,
                               line_xpos, q1_fence_pos,
                               line_xpos + 5, q1_fence_pos,
                               line_xpos - 5, q1_fence_pos,
                               fill=color)
            #~ IR ---
            canvas.create_rectangle(line_xpos - 5, q3_pos,
                                    line_xpos + 5, q1_pos,
                                    fill=color, outline=color)
            canvas.create_text(line_xpos - 15, q3_pos, text='Q3',
                               anchor=tk.NE, fill=color, font=stats_font)
            canvas.create_text(line_xpos + 15, q3_pos, text=q3_value,
                               anchor=tk.NW, fill=color, font=stats_font)
            canvas.create_text(line_xpos - 15, q1_pos, text='Q1',
                               anchor=tk.SE, fill=color, font=stats_font)
            canvas.create_text(line_xpos + 15, q1_pos, text=q1_value,
                               anchor=tk.SW, fill=color, font=stats_font)
            #~ Median ---
            canvas.create_line(line_xpos - 5, q2_pos, line_xpos + 6, q2_pos,
                               fill=color_fg, width=1)
            canvas.create_text(line_xpos - 15, q2_pos, text='median',
                               anchor=tk.E, fill=color_fg, font=stats_font)
            canvas.create_text(line_xpos + 15, q2_pos, text=q2_value,
                               anchor=tk.W, fill=color_fg, font=stats_font)
            #~ Max, Min, Range, IQ range values, ... ---
            canvas.create_text(line_xpos + 95, 30,
                               text='MAX:       %s' % (max_value),
                               anchor=tk.W, fill=color_fg, font=stats_font)
            canvas.create_text(line_xpos + 95, 50,
                               text='MIN:       %s' % (min_value), 
                               anchor=tk.W, fill=color_fg, font=stats_font)
            canvas.create_text(line_xpos + 95, 80,
                               text='Range:       %s' % (value_range), 
                               anchor=tk.W, fill=color_fg, font=stats_font)
            canvas.create_text(line_xpos + 95, 100,
                               text='Mid-range:  %s' % (midrange), 
                               anchor=tk.W, fill=color_fg, font=stats_font)
            canvas.create_text(line_xpos + 95, 120,
                               text='IQR:           %s' % (iq_range),
                               anchor=tk.W, fill=color, font=stats_font)
            canvas.create_text(line_xpos + 95, 140,
                               text='Midhinge:    %s' % (midhinge),
                               anchor=tk.W, fill=color, font=stats_font)
            canvas.create_text(line_xpos + 95, 160,
                               text='Trimean:     %s' % (trimean),
                               anchor=tk.W, fill=color, font=stats_font)
            
            #~ drawing_time = time.time() - start
            #~ print "drawing stats time: %s" % drawing_time

        if type(values[0]) == str or type(values[0]) == unicode:
            characterize_str(values)
            
        else:
            characterize_num(values)
        
    def populate_projinfotab(self, geoprojfile):
        parent = self.parent
        path_list, name, ext = parent.fileops.get_file_namelist(geoprojfile)
        self.projinfotab_geofile = geoprojfile

        parent.geoprojfile_layers_schema.delete(*parent.geoprojfile_layers_schema.get_children())
        
        '''
        TODO: Separate module to get layers info ~ProjectFileReader
              add methods to get more qgis project info (layers,...)
              add methods to get gvsig project info
              add methods to get arcgis project info
              add support different projs files versions
        '''        
        layers = []
        dom = dom_parse(geoprojfile)

        if geoprojfile.endswith('qgs'):
            nodes = dom.getElementsByTagName("legendlayer")
            nodes_no = len(nodes)
            for i in range(nodes_no):
                item = nodes.item(i)
                layer = item.attributes['name'].value
                layers.append(layer)

        #~ FIX: find a better way to get gvp project info...
        #~ FIX: group/separate layers by MapContext
        elif geoprojfile.endswith('gvp'):
            xmltags = dom.getElementsByTagName("xml-tag")
            for tag in xmltags:
                try:
                    element = tag.childNodes[1].attributes["value"].value
                except:
                    pass

                if element == 'com.iver.cit.gvsig.fmap.MapContext':
                    flayers = tag.getElementsByTagName("xml-tag")[2]
                    flayers_nodes = flayers.getElementsByTagName("property")
                    for node in flayers_nodes:
                        if node.attributes["key"].value == 'LayerNames':
                            layer_str = node.attributes['value'].value
                            layer_list = layer_str.split(' ,')
                            for gvplayer in layer_list:
                                layers.append(gvplayer)
            
        if len(layers) != 0:
            for layer in layers:
                parent.geoprojfile_layers_schema.insert('', 'end',
                                                        text=layer)
                                                        #~ values=layer)
                                                        
            first = parent.geoprojfile_layers_schema.get_children()[0]                                            
            parent.geoprojfile_layers_schema.selection_set(first)
            #~ parent.geoprojfile_layers_schema.focus_set()
            #~ parent.geoprojfile_layers_schema.focus(first)
      
        #~ parent.projgeofile_layers_schema.bind('<<TreeviewSelect>>', ???)
            
        else:
            no_layers_txt = _("No layers")
            parent.geoprojfile_layers_schema.insert('', 'end',
                                                    text=no_layers_txt)
        
    def update_history(self, cur_dir):
        '''History update...'''
        if not self.parent.backdirs \
        or self.parent.backdirs[-1] != cur_dir:
            self.parent.backdirs.append(cur_dir)
            #~ Adding one because current dir is also in backdirs:
            lim = self.parent.history_limit + 1
            self.parent.backdirs = self.parent.backdirs[-lim:]
                
    def update_list(self, event):
        tree = event.widget
        self.populate_list(tree.focus())
        
    def draw_preview(self, geofile):
        msg = _("Drawing preview")
        logging.info(msg)
        self.parent.add_status_text(msg)
        #~ queue = Queue.Queue()
        plot = PreviewPlot(self.parent, geofile)
        #~ plot = PreviewPlot(self.parent, queue)
        self.plot = plot
        plot.setDaemon(True)
        plot.start()
        #~ queue.put(geofile)
        
    def stop_draw_preview(self, *event):
        self.plot.stop()
        msg = _("Preview stopped")
        logging.info(msg)
        self.parent.add_status_text(msg)
        
    def exec_bookmark(self, event):
        tree = event.widget
        sel_item = tree.focus()
        bookmark_path = str(tree.item(sel_item)['values'][0])
        if tree.focus() != 'Bookmarks':
            try:
                self.parent.event.change_rootdir(bookmark_path)
                self.parent.n1.select(1)
            except Exception, e:
                logging.error(e)
                self.parent.add_status_text(e)
        
    def select_bookmark(self, event):
        tree = event.widget
        sel_item = tree.focus()
        bookmark = tree.item(sel_item)['text']

        if bookmark != self.user_bookmark_name:
            bookmark_path = str(tree.item(sel_item)['values'][0])
            self.parent.rootdir = bookmark_path
            self.populate_list('root', pop_path=bookmark_path)
        
    def populate_bookmarks_tree(self, *event):
        config_default_homedir = self.parent.config_default_homedir
        default_homedir = self.parent.default_homedir
        bookmarks = self.parent.default_bookmarks
        bookmarktree = self.parent.bookmarks
        bookmarktree.delete(*bookmarktree.get_children())

        bookmarktree.insert('', 'end', 'Home', text=_("Home"),
                        image=self.parent.iconhome,
                        values=[unicode(config_default_homedir, "utf-8"),
                                'home'])
           
        if default_homedir != config_default_homedir:
            bookmarktree.insert('', 'end',
                                text=_("Session Home"),
                                image=self.parent.iconhometmp,
                                values=[unicode(default_homedir, "utf-8"),
                                        'shome'])

        lastdir = self.parent.last_dir
        bookmarktree.insert('', 'end', 'Lastsession',
                            text=_("Last session"),
                            image=self.parent.iconlastdir,
                            values=[unicode(lastdir, "utf-8"),
                                'last'])
        
        self.user_bookmark_name = _("User bookmarks") 
        bookmarktree.insert('', 'end', 'Bookmarks', open=True,
                        text=self.user_bookmark_name,
                        image=self.parent.iconbookmarks)
        
        self.populate_bookmarks(bookmarktree, bookmarks, 'Bookmarks')
        
        bookmarktree.focus('Home')
        bookmarktree.pack(side='left', fill='both', expand=1)
        
    def populate_bookmarks(self, tree, bookmarks, parent):
        bookmarks_keys = bookmarks.keys()
        bookmarks_keys.sort()
        
        for bkmrk_id in bookmarks_keys:
            bkmrk_name = bookmarks[bkmrk_id][0]
            bkmrk_path = bookmarks[bkmrk_id][1]

            if os.path.exists(bkmrk_path):
                icon = self.parent.iconfolder
            else:
                icon = self.parent.iconbookmarkerr

            tree.insert(parent, 'end', text=bkmrk_name, image=icon,
                        values=[unicode(bkmrk_path, "utf-8"), bkmrk_id])
        
    def populate_tools(self):
        tooltree = self.parent.tooltree
        tooltree.delete(*tooltree.get_children())
        
        ship_path = self.parent.ship_path
        tools_folder = "%s/%s" % (ship_path, 'tools')
        dirs = os.listdir(tools_folder)
        dirs.sort(key=lambda x: x.lower())
        for folder in dirs:
            exp = '*/%s/icon.gif' % folder
            iconimage = glob(exp)
            if iconimage:
                iconimage = iconimage[0]
                icon = tk.PhotoImage(file=iconimage)
            
            else:
                icon = self.parent.iconship
            tooltree.insert('', 'end', text=folder,
                            image=icon)
                            
        tooltree.pack(side='left', fill='both', expand=1)
        
    def populate_tree(self, tree, node):
        if tree.set(node, "type") != 'directory':
            return
        
        path = tree.set(node, "path")
        tree.delete(*tree.get_children(node))

        childslist = os.listdir(path)
        childslist.sort(key=lambda x: x.lower())
        
        geo_proj_exts = ['.qgs', '.gvp']
        #~ TODO: Add mxd proj ext
        #~ geo_proj_exts = ['.qgs', '.gvp', '.mxd']
        table_exts = ['.csv']
     
        for child_name in childslist:
            child_path = os.path.join(path, child_name).replace('\\', '/')

            if os.path.isdir(child_path):
                child_type = "directory"
                if os.path.islink(child_path):
                    icon = self.parent.iconfoldergo
                elif child_path.endswith('gdb') \
                or child_path.endswith('nd'):
                    icon = self.parent.icongdb
                else:
                    icon = self.parent.iconfolder
                                 
            #~ TODO: add ext list with table files
            elif os.path.isfile(child_path):
                namelist = os.path.splitext(child_name)
                ext = namelist[1].lower()

                #~ FIX: make functional ----
                if ext == '.shp':
                    child_name = namelist[0]
                    icon = self.parent.iconshape
                    child_type = "shape"
                    shp_err = "%s.err" % (child_path)
                    if glob(shp_err):
                        icon = self.parent.iconshapeerr
                        child_type = "shape_err"
                
                elif ext == '.zip' and namelist[0][-4:] == '.shp':
                    child_name = namelist[0][:-4]
                    icon = self.parent.iconshpzip
                    child_type = "shpzip"
                    shpzip_err = "%s.err" % (child_path)
                    if glob(shpzip_err):
                        icon = self.parent.iconshpziperr
                        child_type = "shpzip_err"
                
                elif ext == '.sqlite' or ext == '.db':
                    child_name = namelist[0]
                    icon = self.parent.icondb

                    db = shapedb.DbReader(child_path)
                    if db.check_ogr_format():
                        db = shapedb.ShapedbReader(child_path)
                        child_type = "sqliteshp"
                    else: 
                        child_type = "sqlite"
                    db_err = "%s.err" % (child_path)
                    if glob(db_err):
                        icon = self.parent.icondatabaseerr
                        child_type = "sqlite_err"
                        
                elif ext == '.zip' \
                and (namelist[0][-7:] == '.sqlite' \
                     or namelist[0][-2:] == 'db'):
                        child_name = os.path.splitext(namelist[0])[0]
                        icon = self.parent.icondbzip
                        child_type = "sqlitezip"
                        #~ TODO: sqlite/db.zip.err
                    
                elif ext == '.shz':
                    child_name = namelist[0]
                    icon = self.parent.iconshz
                    child_type = "shapeezy"
                    #~ TODO: SHZ error ?
                    #~ shz_err = "%s.err" % (child_path)
                    #~ if glob(shz_err):
                        #~ icon = self.parent.iconshapeerr
                        #~ child_type = "shz_err"

                #~ TODO: ? elif  gdb (spatial-geo database), geopackage
                #~ elif ext == '.gdb'
                
                elif ext == '.gpkg':
                    child_name = namelist[0]
                    child_type = "geopkg"
                    icon = self.parent.icongpkg
                    db = shapedb.DbReader(child_path)
                    
                elif ext in geo_proj_exts:
                    child_name = namelist[0]
                    child_type = "geoproj"
                    if namelist[1] == '.gvp':
                        icon = self.parent.icongvp
                    elif namelist[1] == '.qgs':
                        icon = self.parent.iconqgs
                    elif namelist[1] == '.mxd':
                        icon = self.parent.iconmxd
                
                elif ext in table_exts:
                    child_name = '%s [%s]' % (namelist[0],
                                              namelist[1][-3:])
                    child_type = "table"
                    icon = self.parent.icontable
                    
                else:
                    #~ child_type = "file"
                    continue

                #~ -------------------------
     
            id = tree.insert(node, "end", text=child_name, image=icon,
                             values=[unicode(child_path, "utf-8"),
                                     child_type])
     
            if child_type == 'directory':
                dirpath = tree.item(id)['values'][0]
                #~ tree.item(id, text=child_name)
                try:
                    contents = os.listdir(dirpath)
                    #~ FIX: don't show expansion arrow if there is not
                    #~ viewable contents (folders or shp/db/csv...) ??
                    if len(contents) > 0:
                        #~ Void folder simulated to add open/close bullet:
                        tree.insert(id, 0, text="dummy")
                except Exception, e:
                    logging.error(e)
                    self.parent.add_status_text(e)
            elif child_type == 'sqlite' \
            or child_type == 'geopkg':
                geodbpath = tree.item(id)['values'][0]
                tables = db.tables
                for table in tables:
                    icon = self.parent.icontable
                    child_type = 'sqliteshp'
                    size = 0
                    timestring = ''
                    tree.insert(id, 'end',
                                text=table, image=icon,
                                values=[geodbpath, child_type, size,
                                        timestring])
                
        tree.pack(side='top', fill='both', expand=1)
        
    def update_tree(self, event):
        tree = event.widget
        self.populate_tree(tree, node=tree.focus())
        
    def update_filetree_path_entry(self, event):
        path = event.widget.get()
        self.parent.event.change_rootdir(path)

    def set_tree_root(self, tree, path):
        root = os.path.basename(path)
        icon = self.parent.iconfolder
        
        self.parent.rootdir = path
        
        #~ Combobox filetree_path update
        self.parent.filetree_path_entry.set(path)
        
        tree.delete(*tree.get_children())
        node = tree.insert('', 'end', 'root', text=root, open=True,
                           image=icon, values=[path,
                                               "directory"])
        self.populate_tree(tree, node)

        self.parent.event.tree_focus(tree)


class FileOps():
    ''''''
    def __init__(self, parent):
        self.parent = parent

    def get_selected_items(self, event=None):
        #~ TODO: if event:
        wdgt = self.parent.filelist
        selection = wdgt.selection()
        
        return wdgt, selection

    def get_file_namelist(self, path):
        path_list = os.path.split(path)
        name, ext = os.path.splitext(path_list[1])

        #~ For names with double extension as shp.xml or aux.xml
        ext_2 = os.path.splitext(name)
        if ext_2[1][1:] in self.parent.doubleexts:
            ext = "%s%s" % (ext_2[1], ext)
            name = ext_2[0]
            
        ext = ext[1:].lower()
        return path_list, name, ext
        
    def update_after_fileop(self):
        nb = self.parent.n1
        if nb.select() == nb.tabs()[1]:
            self.parent.event.change_rootdir(self.parent.current_dir)
            self.parent.event.get_list_focus()
        else:
            #~ # Update list
            cur_dir = self.parent.current_dir
            filenav = self.parent.filenav
            filenav.populate_list('root', pop_path=cur_dir)
            self.parent.event.get_list_focus()

    def add_shape_files(self, path_list, name, ext):
        if self.parent.shapemode and ext == 'shp':
            # FIX: ? loop
            for ext in self.parent.shpexts:
                shape_item = "%s/%s.%s" % (path_list[0],
                                           name, ext)
                if os.path.exists(shape_item):
                    self.parent.fileop_items.append(shape_item)
        
    def option_new_folder_name(self, nametomod):
        exists_text = _("The name already exists.")
        choose_text = _("Please choose an alternative name")
        msg = '%s %s.' % (exists_text, choose_text)
        logging.warning(msg)
        self.parent.add_status_text(msg)
        warning = '%s \n%s:' % (exists_text, choose_text)
        new_name = self.set_name(_("Name conflict"), warning, nametomod,
                                 self.parent)
        if new_name:
            msg = "%s: %s" % (_("New folder"), new_name)
            logging.info(msg)
            self.parent.add_status_text(msg)
            return new_name
            
    #~ TODO: To class in gui.py
    def fileoption_dialog(self, title, message):
        top = tk.Toplevel(self.parent)
        top.wm_title(title)
        top.resizable(0, 0)

        #~ FIX: Add icon="warning"
        label = ttk.Label(top, text=message)
        label.pack(padx=10, pady=5)

        allvar = tk.BooleanVar()
        
        def on_apply_all():
            if allvar.get() == True:
                self.option_overwrite_all = True

        apply_text = _("Apply this action to all elements")
        all_chbtn = ttk.Checkbutton(top, text=apply_text,
                                    command=on_apply_all,
                                    variable=allvar)
        all_chbtn.pack(side='left', padx=5, pady=5)

        def on_ok():
            self.overwrite = True
            top.destroy()
        
        def on_no():
            self.overwrite = False
            top.destroy()

        b_yes = ttk.Button(top, text=_("Yes"), command=on_ok)
        b_yes.pack(side='right', padx=5, pady=5)
        b_no = ttk.Button(top, text=_("No"), command=on_no)
        b_no.pack(side='right', padx=5, pady=5)
        
        top.transient(self.parent)        
        top.grab_set()
        self.parent.center_window(top)
        self.parent.wait_window(top)
        
    #~ def option_apply_to_all(self):
        #~ TODO: include as checkbox in merge/overwrite dialogs
        #~       -> custom dialogs?
        #~ print "Apply this action to all elements?..."
        #~ warning = ("Appy this action to all elements?")
        #~ 
        #~ apply_all = messagebox.askyesno("Appy to all", warning,
                                        #~ icon="warning")
        #~ return apply_all
            
    def option_merge_folders(self):
        exists_text = _("A folder with the same name already exists.")
        merge_text = _("Do you want to merge this folders?")
        msg = "%s %s" % (exists_text, merge_text)
        logging.warning(msg)
        self.parent.add_status_text(msg)
        warning = "%s \n%s" % (exists_text, merge_text)

        self.fileoption_dialog(_("Merge folders"), warning)

        #~ merge = messagebox.askyesno("Merge folders", warning,
                                    #~ icon="warning")
        #~ apply_all = self.option_apply_to_all()
        #~ 
        #~ if apply_all:
            #~ self.option_merge_all = True
            #~ 
        #~ return merge
        
    def option_overwrite_files(self):
        exists_text = _("A file with the same name already exists.")
        overwr_text = _("Do you want to overwrite this file?")
        msg = "%s %s" % (exists_text, overwr_text)
        logging.warning(msg)
        self.parent.add_status_text(msg)
        warning = "%s \n%s" % (exists_text, overwr_text)
        
        self.fileoption_dialog(_("Overwrite files"), warning)
        #~ TODO: Shapefiles: apply all by default for shpexts?
                   
        #~ overwrite = messagebox.askyesno("Overwrite files", warning,
                                    #~ icon="warning")

        #~ if len(self.parent.fileop_items) > 1:
            #~ apply_all = self.option_apply_to_all()
        #~ else:
            #~ apply_all = None
            #~ 
        #~ if apply_all:
            #~ self.option_overwrite_all = True
        #~ 
        #~ return overwrite
            
    def handle_name_exception(self, fn, path, dst, move=False):
        #~ FIX: Make unittests
        #~ FIX: ? Decorator?
        #~ def wrapped():
        name = os.path.basename(path)
            
        #~ TODO: merge folders
        #~ if os.path.isdir(path) \
        #~ and not self.option_merge_all:
            #~ merge = self.option_merge_folders()
            #~ if merge:
                #~ prev_dst = self.dst
                #~ self.dst = "%s/%s" % (self.dst, name)
                #~ childs = os.listdir(path)
                #~ elements = map(lambda child: os.path.join(path, child),
                              #~ childs)
                #~ map(lambda path: self.paste_element(path), elements)
                #~ self.dst = prev_dst
                # self.delete_element(path)

                #~ print "Folders merged"
                #~ return

        while True:
            if move:
                new_dst = "%s/%s_copy" % (dst, name)
                name += "_copy"
            
            else:
                new_name = self.option_new_folder_name(name)
            
                if not new_name:
                    break
            
                new_dst = "%s/%s" % (dst, new_name)
            
            try:
                msg = "%s %s to %s" % (_("Copied"), path, new_dst)
                logging.info(msg)
                self.parent.add_status_text(msg)
                fn(path, new_dst)
                
            except Exception, e:
                '''
                exceptions:
                OSError [Errno 17] File exists
                IOError [Errno 21] Is a directory for existent folder.
                shutil.Error Destination path "x" already exists.
                '''
                msg = "%s %s" % (_("Name already exists."), e)
                logging.warning(msg)
                self.parent.add_status_text(msg)
                #~ FIX: file -> folder don't repeat loop
                continue
                
            else:
                break
                    
        #~ return wrapped
    
    def set_fileop_items(self, event=None, cut=False):
        wdgt, selection = self.get_selected_items(event)

        self.parent.fileop_items = []
        
        self.parent.cut = False
        if cut == True:
            self.parent.cut = True
        
        def add_fileop_items(sel_item):
            item_path = wdgt.item(sel_item)['values'][0]
            self.parent.fileop_items.append(item_path)
            
        map(add_fileop_items, selection)

    def copy_elements(self, event=None):
        self.set_fileop_items(event)
        
    def cut_elements(self, event=None):
        self.set_fileop_items(event, True)
        
    def paste_element(self, item_path, rename=None):
        path_list, name, ext = self.get_file_namelist(item_path)
        self.add_shape_files(path_list, name, ext)
        dst = self.dst

        if rename:
            dst = "%s/%s" % (path_list[0], rename)
            if self.parent.shapemode \
            and (ext == 'shp' or ext in self.parent.shpexts):
                dst = "%s.%s" % (dst, ext)
    
        #~ "if copy"
        if not self.parent.cut:

            #~ "if dir"
            if os.path.isdir(item_path):
                dst_name = "%s/%s" % (dst, name)
                msg = "%s %s to %s" % (_("Copied"), item_path, dst_name)
                logging.info(msg)
                self.parent.add_status_text(msg)
                try:
                    #~ copytree: dir -> dst/dir
                    shutil.copytree(item_path, dst_name)
                
                except Exception, e:
                    '''
                    folder -> folder/dir
                    exception if file or folder name exists
                    exception [Errno 17] File exists
                    '''
                    logging.error(e)
                    self.parent.add_status_text(e)
                    self.handle_name_exception(shutil.copytree,
                                               item_path,
                                               dst)
                    #~ self.handle_name_exception(shutil.copytree(item_path,
                    #~                            "%s/%s" % (dst, new_name)))
                
            #~ "if file"
            else:
                dst_name = "%s/%s" % (dst, path_list[1])
                msg = "%s %s to %s/%s" % (_("Copied"), item_path, dst,
                                          dst_name)
                logging.info(msg)
                self.parent.add_status_text(msg)
                
                if os.path.exists(dst_name) \
                and os.path.isfile(dst_name):
                    if not self.option_overwrite_all:
                        #~ self.overwrite = self.option_overwrite_files()
                        self.option_overwrite_files()
                    if not self.overwrite:
                        msg = _("File not overwritten (not copied)")
                        logging.info(msg)
                        self.parent.add_status_text(msg)
                        return
                    #~ FIX: if ext shp -> check by default
                    #~      apply to all files
                try:
                    shutil.copy(item_path, dst)
                
                except Exception, e:
                    logging.error(e)
                    self.parent.add_status_text(e)
                    self.handle_name_exception(shutil.copy,
                                               item_path,
                                               dst)
                
        #~ "if cut"
        else:
            msg = "%s %s %s %s" % (_("Cut from"), item_path, _("to"), dst)
            logging.info(msg)
            self.parent.add_status_text(msg)
            try:
                shutil.move(item_path, dst)
            
            except Exception, e:
                logging.error(e)
                self.parent.add_status_text(e)
                '''
                file or folder -> folder
                exception if file or folder name exists
                exception shutil.Error Destination path ""
                                       already exists.
                The destination directory must not already
                exist. If the destination already exists but
                is not a directory, it may be overwritten
                depending on os.rename() semantics.
                FIX: ?
                '''
                self.handle_name_exception(shutil.move,
                                           item_path,
                                           dst, True)
                    
    def paste_elements(self, event=None, rename=None, elements=None):
        self.option_overwrite_all = False
        self.option_merge_all = False
        
        if not elements:
            elements = self.parent.fileop_items
        #~ FIX: Make unittests
        if self.parent.fileop_items:
            self.dst = self.parent.current_dir
            
            if os.path.isdir(self.dst):
                map(lambda path: self.paste_element(path, rename),
                    elements)
                
            self.update_after_fileop()
                
    def set_name(self, title, text, default_value, wparent):
        #~ FIX: Center dialog
        new_name = simpledialog.askstring(title, text,
                                          initialvalue=default_value,
                                          parent=wparent)
        if new_name:
            return new_name

    def rename_elements(self, event):
        wdgt = event.widget
        sel_item = wdgt.selection()[0]
        item_path = wdgt.item(sel_item)['values'][0]
        old_name = wdgt.item(sel_item)['text']
        path_list, name, ext = self.get_file_namelist(item_path)

        '''
        This avoid extension renaming to .shp and shpexts files in
        shapemode. If the user wants to rename this extensions she
        have to change to non-shapemode. FIX ?
        '''
        if self.parent.shapemode \
        and (ext == 'shp' or ext in self.parent.shpexts):
            old_name = name
        
        new_name = self.set_name(_("Rename"), _("New name:"), old_name,
                                 self.parent)

        if new_name:
            self.cut_elements(event)
            self.paste_elements(event, rename=new_name)
            self.parent.fileop_items = []

    def new_folder(self):
        path = self.parent.current_dir
        
        new_folder = self.set_name(_("New folder"), _("Folder name:"),
                                   _("Untitled_folder"), self.parent)
    
        full_path_folder = os.path.join(path, new_folder)
        
        try:
            os.mkdir(full_path_folder)
                
        except OSError, e: # [Errno 17] File exists
            #~ TODO: method (decorator?)
            #~ FIX: warn to status bar message
            msg = "%s %s" % (_("File exists."), e)
            logging.error(msg)
            self.parent.add_status_text(msg)
            copyno = 1
            while True:
                new_folder_copy = self.set_name(_("New folder"),
                                                _("Folder name:"),
                                                "%s_copy_%s" % (new_folder,
                                                                copyno),
                                                self.parent)
                                   
                full_path_folder = os.path.join(path, new_folder_copy)
                                             
                try:
                    os.mkdir(full_path_folder)
                    
                except OSError, e: # [Errno 17] File exists:
                    msg = "%s %s" % (_("File exists."), e)
                    logging.error(msg)
                    self.parent.add_status_text(msg)
                    copyno += 1

                else:
                    break
        
        self.update_after_fileop()
    
    def delete_element(self, item_path):
        path_list, name, ext = self.get_file_namelist(item_path)
        self.add_shape_files(path_list, name, ext)
        
        if os.path.isfile(item_path):
            try:
                os.remove(item_path)
                #~ TODO: ??? Move to system trash instead?
            
            except:
                #~ TODO: Exception handling
                raise
                
        elif os.path.isdir(item_path):
            try:
                shutil.rmtree(item_path)
                #~ TODO: ??? Move to system trash instead?
            
            except:
                #~ TODO: Exception handling
                raise
                
        self.update_after_fileop()

    def delete_elements(self, event):
        if self.parent.filelist.selection():
            delete_text = _("This will delete the selection.")
            sure_text = _("Are you sure to proceed?")
            warning = "%s\n%s" % (delete_text, sure_text)
            confirmation = messagebox.askokcancel(_("Delete"), warning,
                                                  icon="warning")
                       
            if not confirmation:
                return
            
            self.set_fileop_items(event)
                
            map(self.delete_element, self.parent.fileop_items)
                
            self.update_after_fileop()
            
            #~ TODO: Send message to StatusBar:
                #~ print "Selection Deleted"
                #~ print itempath, "Removed"

    def read_geozip_file(self, geozipfile):
        geozipfile_name = os.path.basename(geozipfile)
        geofile_shp = os.path.splitext(geozipfile_name)[0]
        geofile_dbf = "%s.%s" % (os.path.splitext(geofile_shp)[0],
                                "dbf")
        geofile_shx = "%s.%s" % (os.path.splitext(geofile_shp)[0],
                                 "shx")
        tmpdir = temp_mkdtemp()
                
        with zipfile(geozipfile, 'r') as shpzip:
            shpzip.extract(geofile_shp, tmpdir)
            shpzip.extract(geofile_dbf, tmpdir)
            shpzip.extract(geofile_shx, tmpdir)
                    
        geofile = "%s/%s" % (tmpdir, geofile_shp)
        geofile_data = shape.ShapeReader(geofile)
                    
        shutil.rmtree(tmpdir)
        return geofile_data
        
    def compress_element(self):
        pass
        #~ shutil.make_archive(base_name, format
        #~ "You can register new formats or provide your own archiver
        #~ for any existing formats, by using register_archive_format()"
        
    def decompress_element(self):
        pass
