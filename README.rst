.. -*- restructuredtext -*-

=========================
Ship-Shape-File-Navigator
=========================

Intro
=====

Ship-Shape-File-Navigator (Ship) is a standalone FLOSS navigational file manager focused to ease the management of Shapefile files, a de-facto standard format to handle GIS data.

Ship allows you navigate through directories and see shapefile's (and some other geographic formats as well) main characteristics, tabular data, and a preview of their geometries.

With Ship you'll be able to do common file operations like copy, move, rename and delete to the shapefiles as a whole (and soon also apply batch geoprocessing to them).

============ ==========
**Version:** 0.1 alpha
**Author:**  Adrian Eiris Torres (adrianet82[at]gmail.com)
**License:** GNU GENERAL PUBLIC LICENSE Version 3
**URL:**     http://www.shipshapefilenavigator.org
============ ==========


Installing
==========

Ship-Shape-File-Navigator only requires Python 2.7 with Tkinter so it doesn't require installation but having those in your system.

Windows users only require a Python 2.7 interpreter.
Linux users should have Python already installed but may have to install 'python-tk' package (apt-get intall python-tk, yum...).

Extract Ship to some place in your system and run the shipshpfn/gui.py file,

Windows
-------

Execute the shipshpfn/gui.py by double click on the file or through console:

C:\\[path_to_Ship]\\shipshpfn\\gui.py

(If you want to avoid the console window just change "gui.py" name to "gui.pyw" and run as before).


Linux
-----

from the Ship folder:

python shipshpfn/gui.py


or another path:

python [path_to_Ship]/shipshpfn/gui.py


More details in the project documentation:

local: docs/_build/html/installation.html

online: http://shipshapefilenavigator.readthedocs.io/en/latest/installation.html


Contributing
============

Please read the contributing section in the project documentation:

local docs: docs/_build/html/contribution.html

or online: http://shipshapefilenavigator.readthedocs.io/en/latest/contribution.html

