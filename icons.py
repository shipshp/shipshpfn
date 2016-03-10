
"""\
########################################################################
  Ship-Shape-File-Navigator
########################################################################

Ship Shapefile Navigator website: www.shipshapefilenavigator.org
If you find any bugs or have any suggestions you could email to the
project mail list: @shipshapefilenavigator.org

Copyright (C) 2013 Adrian E <@.org>

This program is free software: you can redistribute it and/or modify 
it under the terms of the GNU General Public License as published by 
the Free Software Foundation, either version 3 of the License, or 
(at your option) any later version.

This program is distributed in the hope that it will be useful, 
but WITHOUT ANY WARRANTY; without even the implied warranty of 
MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE.  See the 
GNU General Public License for more details.

You should have received a copy of the GNU General Public License 
along with this program.  If not, see <http://www.gnu.org/licenses/>
########################################################################
"""

#~ -----------------------------------------------------------
#~ Icons used in Ship are mostly from this beautiful icon set
#~ (then converted to .gif and some slightly modified):
#~ 
#~ Silk icon set 1.3
#~ Mark James
#~ http://www.famfamfam.com/lab/icons/silk/
#~ 
#~ Also there are icons taken from:
#~ Tango Icon Theme (tango-icon-theme-0.8.90)
#~ http://tango.freedesktop.org/
#~ -----------------------------------------------------------

#~ (icons in ./icons, .gif extension)

#~ App main icons -----------------------------
#~ Folders:             folder
#~ Files without ext:   page_white
#~ Shapefiles:          layers
#~ Ship icon:           ship (Ship self-made)
#~ --------------------------------------------

mainicons =     [('iconfolder',      'folder'),
                 ('iconfoldergo',    'folder_go'),
                 ('iconfile',        'page_white'),
                 ('iconstar',        'star'),
                 ('iconshape',       'layers'),
                 ('iconshapeerr',    'shapeerr'),
                 ('iconshpzip',      'shapezip'),
                 ('iconshpziperr',   'shapeziperr'),
                 ('icondb',          'database'),
                 ('icondatabaseerr', 'database_error'),
                 ('icondbzip',       'databasezip'),
                 ('iconshz',         'shapeezy'),
                 ('iconerror',       'page_white_error'),
                 ('shipabout',       'about'),
                 ('iconship',        'ship'),
                 ('iconshipbig',     'shipb')]

appicons = {
                'back': 'bullet_back',
                'bookmarks': 'folder_star',
                'bookmarkerr': 'page_white_error',
                'content': 'application_view_list',
                'conttable': 'cont-table',                 #~ (mod-Silk)
                'copy': 'page_copy',
                'cut': 'cut_red',
                'exit': 'door_out',
                'fwrd': 'bullet_go',
                'hash': 'hash',                            #~ (Ship)
                'help': 'help',
                'home': 'house',
                'hometmp': 'application_home',
                'info': 'information',
                'lastdir': 'time_back',
                'opendir': 'folder_explore',
                'paste': 'page_white_paste',
                'prefs': 'wrench',
                'preview': 'map',
                'selall': 'selall',                        #~ (mod-Silk)
                'selinvert': 'refresh_arrows',
                'setfirst': 'resultset_first',
                'setlast': 'resultset_last',
                'setnext': 'resultset_next',
                'setprev': 'resultset_previous',
                'table': 'table',
                'tableinfo': 'tableinfo',                  #~ (mod-Silk)
                'tableedit': 'table_edit',
                'term': 'terminal',                        #~ (Tango)
                'toolbar': 'tools_panel',                  #~ (mod-Silk)
                'tools': 'cog',
                'tree': 'tree',                            #~ (mod-Silk)
                'treepanel': 'application_side_tree',
                'up': 'bullet_up',
            }


#~ Formats-icons relation:

#~              ext : filename
#~-------------------------------- 
fileicons = {
                'shp': 'layers',
                'shx': 'page_white_key',
                'dbf': 'table',
                'prj': 'page_white_world',
                'shp7z': 'shapezip',                       #~ (mod-Silk)
                #~ 'shpzip': 'shapezip',                   #~ (mod-Silk)
                #~ 'tool': 'tool',
                #~ 'toolset': 'toolset',
                #~ ----------------------
                'bmp': 'image',
                'dgn': 'page_white_vector', #temp
                'dwg': 'page_white_vector', #temp
                'dxf': 'page_white_vector', #temp
                'cdr': 'page_white_vector',
                'css': 'page_white_code',
                'csv': 'table',             #temp
                'db': 'database',
                'dberr': 'page_white_error',
                'doc': 'page_word',
                'docx': 'page_word',
                'ecw': 'map',
                'eps': 'page_white_vector',
                'err': 'page_white_error',
                'shperr': 'page_white_error',
                'exe': 'binary',                           #~ (Tango)
                'gdb': 'database',
                'gif': 'image',
                'gpkg': 'geopkg',                          #~ (mod-Silk)
                'gvp': 'gvsig',                            #~ (gvSIG)
                #~ 'gxw': 'grass',
                'gz': 'compress',
                'html': 'page_white_code',
                'ico': 'image',
                'jar': 'page_white_cup',
                'jpg': 'image',
                'jpeg': 'image',
                'js': 'page_white_code',
                'json': 'page_white_code',
                'kml': 'gearth',                           #~ (Google)
                'kmz': 'gearth',                           #~ (Google)
                'log': 'page_white_text',
                'mxd': 'esrimxd',                          #~ (Ship)
                'odt': 'document',                         #~ (Tango)
                'ods': 'spreadsheet',                      #~ (Tango)
                'pdf': 'page_white_acrobat',
                'pgm': 'image',
                'php': 'page_white_code',
                'png': 'image',
                'pnm': 'image',
                'ppm': 'image',
                'ppt': 'presentation',                     #~ (Tango)
                'pps': 'presentation',                     #~ (Tango)
                'py': 'python',                            #~ (Python)
                'pyc': 'pythonc',       
                'qgs': 'qgis',                             #~ (QGIS)
                #~ 'qml': 'grass',
                'rar': 'compress',
                'sprj': 'saga',                            #~ (SAGA)
                'sqlite': 'database',
                'sqliteerr': 'page_white_error',
                'sqlite3': 'database',
                'sh': 'page_white_code',
                'so': 'page_white_code',
                'svg': 'page_white_vector',
                'tar': 'compress',          #temp
                'tgz': 'compress',
                'tif': 'map',
                'txt': 'text',                             #~ (Tango)
                'xls': 'page_excel',
                'xml': 'page_white_code',
                'zip': 'compress',
            }

#~ --------------------------
#~ TODO: Add following formats:
#~ 
#~ mdb
#~ (CAD: dwg,dgn,dxf,(dwl)) *sdf spatial data file
#~ RASTER: mrsid,aux,rmf,rrd,tfwx,tif.xml
#~ Lidar: las,laz
#~ ESRI: lyr (?):sbn,sbx,nd,nds,csf,shp.aig?,mxt(template)
#~ Geomedia: gws
#~ OSM ?, gpx
#~ shz, fdb?, alias(elle?),xsd, gvl
#~ ps,rtf,wmf,emf
#~ xcf(gimp),photoshop
#~ ini,bat,bak
#~ raster double / triple extensions (tiff.aux.xml)
    
