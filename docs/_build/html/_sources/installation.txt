
.. _installation:


============
Installation
============

Ship-Shape-File-Navigator doesn't require installation but requires a Python 2.7 interpreter with Tkinter.

If you have those in your system just `get Ship <http://shipshp.bitbucket.org/downloads.html>`_, extract it to some place and run the **shipshpfn/gui.py** file,


from the Ship folder:

.. code-block:: bash

    python shipshpfn/gui.py


or another path:

.. code-block:: bash

    python [path_to_Ship]/shipshpfn/gui.py



Windows users
=============

.. [Download the executable file]

If you don't have a python interpreter installed in your system, you can install the official Python interpreter (2.7 version) getting it from:

official Python web: https://www.python.org/downloads/release/python-2711/

.. _`32 bit`: https://www.python.org/ftp/python/2.7.11/python-2.7.11.msi
.. _`64 bit`: https://www.python.org/ftp/python/2.7.11/python-2.7.11.amd64.msi

or direct download from here: `32 bit`_ | `64 bit`_

.. or conda (Anaconda/Miniconda):
.. http://conda.pydata.org/docs/download.html 


Linux users
===========

You should have a Python 2.7 interpreter already installed in your system but some distros may not include the **python-tk** package. In that case you can install it from the repositories:

Debian/Ubuntu/Mint:
-------------------

.. code-block:: bash

    [sudo] apt-get install python-tk

RPM based (Fedora...):
----------------------

.. code-block:: bash

    yum install tkinter


GIT
===

Another way you could get and use Ship is directly from the repository, executing it with Python.

Cloning the repository:

.. code-block:: bash

    git clone https://bitbucket.org/shipshp/shipshpfn.git
    

Executing from the repo folder:

.. code-block:: bash

    python shipshpfn/gui.py

or another path:

.. code-block:: bash

    python [path_to_repo]/shipshpfn/gui.py
    

In this way you may also have access to the latest development state of the application, just changing to the **development** branch:

.. code-block:: bash

    git checkout development


Python distutils/setup tools
============================

.. Not to install: "python setup.py install"
.. Source distribution OK: "python setup.py sdist"


Virtual environments
====================
