#! /usr/bin/env python
# -*- coding: utf-8 -*-

'''
ship styles
'''

import ttk
from platform import system as platform_system


class Style():
    ''''''
    def __init__(self):
        self.style = ttk.Style()
        
        self.bg_color  = '#444643'
        self.bg_clean = '#F0EEF5'
        self.bg_dark_color = '#3B3D3B'
        self.bg_dark2_color = '#2C2E2C'
        #~ self.bg_light_color = '#5C5E5A' # night commander
        self.bg_light_color = '#555753'    # ship default
        self.bg_light2_color = '#646661'
        self.fg_color  = '#F2F1F0'
        self.sel_color = '#94A7C0'
        self.sel_color_dark = '#657182'
        
        opsys = platform_system()
        if opsys != 'Windows':
            self.set_ship_style()
            
    def list_themes(self):
        return self.style.theme_names()

    def change_theme(self, theme):
        self.style.theme_use(theme)

    def set_ship_style(self):
        '''
        Get style info examples -------------------------------------
        s = self.style
        print s.theme_use()
        
        Layouts --
        print s.layout('Treeview')
        result:
        [('Treeview.field',
            {'border': '1', 'children':
                [('Treeview.padding', {'children':
                    [('Treeview.treearea', {'sticky': 'nswe'})],
                'sticky': 'nswe'})],
            'sticky': 'nswe'})]
                    
        Elements --
        print s.element_names()
        print s.element_options('Treeview.field')
        result:
        ('-fieldbackground', '-borderwidth')
        
        Element value --
        print s.lookup('Table.Treeview.field', 'borderwidth')
        result: 1
        
        Style maps --
        s.map("TCombobox", fieldbackground=[("selected", 'red')])
        s.map("TCombobox", fieldbackground=[("!selected", 'blue')])
        ----------------------------------------------------------------
        '''
        '''
        TODO: theme creation
        style = ttk.Style()
        style.theme_settings("default", {
           "TCombobox": {
               "configure": {"padding": 5},
               "map": {
                   "background": [("active", "green2"),
                                  ("!disabled", "green4")],
                   "fieldbackground": [("!disabled", "green3")],
                   "foreground": [("focus", "OliveDrab1"),
                                  ("!disabled", "OliveDrab2")]
               }
           }
        })
        style.theme_create(themename, parent=None, settings=None)
        theme_use(themename=None)
        '''
        fg_color = self.fg_color
        bg_color = self.bg_color
        bg_light_color = self.bg_light_color
        bg_dark_color = self.bg_dark_color
        bg_dark2_color = self.bg_dark2_color
        sel_color = self.sel_color
        
        #~ root style -----
        style = self.style
        style.configure(".",
                    #~ background=bg_color,     # night commander
                    background=bg_light_color,  # ship default
                    fieldbackground=bg_color,
                    foreground=fg_color, 
                    )
        style.map(".", background=[("active", bg_dark_color)])

        #~ notebooks tabs style ----
        #~ nbks_style_name = "Ship.TNotebook"
        #~ nbks_style_name = "Clear.TNotebook"
        #~ s.configure(nbks_style_name,
                    #~ foreground='red')
        style.map("TNotebook.Tab", background=[("selected", bg_light_color),
                                           ("!selected", bg_dark_color)])
                    
        #~ Other elements style ----
        #~ (entry, combo, spin, label, scrollbars)
        for element in ('TEntry', 'TCombobox'):
            style.configure(element,
                        foreground=fg_color, 
                        fieldbackground=bg_light_color
                        )
                    
        #~ s.map("TEntry", fieldbackground=[("readonly", bg_light_color)])
        style.map("TCombobox", fieldbackground=[("!disabled", bg_light_color)])
        
        for scrollbar in ('Horizontal.TScrollbar', 'Vertical.TScrollbar'):
            style.configure(scrollbar, fieldbackground='red', troughcolor=bg_dark2_color)
            style.map(scrollbar, fieldbackground=[("!disabled", bg_light_color)])
            
        #~ -----------------------

        #~ All treeviews
        style.configure("Treeview", background=bg_color, foreground=fg_color)
        style.map("Treeview", background=[("selected", sel_color)])
        
        #~ Filetree style
        style.configure("Ftree.Treeview",
                    #~ foreground=fg_color
                    )
        #~ style.map("Ftree.Treeview", background=[("selected", sel_color)])
                            
        #~ Filelist style
        style.configure("Flist.Treeview",
                    #~ foreground=fg_color
                    )
        #~ style.map("Flist.Treeview", background=[("selected", sel_color)])

        #~ Table style
        #~ Make avaliable to grow-decrease font size (5)-7-12-(14)
        style.configure("Table.Treeview", font=('Sans', 8),
                    #~ background=bg_color, foreground=fg_color
                    )
        #~ style.map("Table.Treeview", background=[("selected", sel_color)])
        
        #~ -----------------------
