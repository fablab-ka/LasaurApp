
LasaurApp
=========

LasaurApp is the official app to control [Lasersaur](http://lasersaur.com) laser cutters. At the moment it has the following features:

- send G-code to the lasersaur
- convert SVG files to G-code
- GUI widget to move the laser head
- handy G-code programs for the optics calibration process

This app is written mostly in cross-platform, cross-browser Javascript. The idea is to use only a lightweight backend for relaying to and from the USB port. Eventually this backend can either move to the controller on the Lasersaur or to a small dedicated computer. 

This is done this way because we imagine laser cutters being shared in shops. We see people  controlling laser cutters from their laptops and not wanting to go through annoying setup processes. Besides this, html-based GUIs are just awesome :)

**DISCLAIMER:** Please be aware that operating a DIY laser cutter can be dangerous and requires full awareness of the risks involved. You build the machine and you will have to make sure it is safe. The instructions of the Lasersaur project and related software come without any warranty or guarantees whatsoever. All information is provided as-is and without claims to mechanical or electrical fitness, safety, or usefulness. You are fully responsible for doing your own evaluations and making sure your system does not burn, blind, or electrocute people.


How to Use this App
-------------------

* make sure you have Python 2.7
* install [pyserial](http://pyserial.sourceforge.net/)
* run *python app.py*
* open *http://localhost:4444* 
  (in current Firefox or Chrome, future Safari 6 or IE 10)

For more information see the [Lasersaur Software Setup Guide](http://labs.nortd.com/lasersaur/manual/software_setup).



Notes on Creating Standalone Apps
----------------------------------

With [PyInstaller](http://www.pyinstaller.org) we can convert a python app to a standalone application. This allows us to make the setup process much easier and remove all the prerequisites on the target machine (including python and pyserial).

From command line interface do the following:

* go to LasaurApp/other directory
* run 'python pyinstaller/pyinstaller.py --onefile app.spec'
* the executable will be in other/dist/

Most of the setup for making this happen is in the app.spec file. Here all the accessory data and frontend files are listed for inclusion in the executable. In the actual code the data root directory can be found in 'sys._MEIPASS'.


Notes on Writing PyQt Apps
----------------------------

PyQt are the python wrappers for the Qt SDK. A good intro is here: http://zetcode.com/tutorials/pyqt4/

### On OSX (64-bit):
  - python 2.7 is already installed
  - install Homebrew
  - use Homebrew to install PyQt (takes a while)
    - "brew install pyqt"
  - need to point python to the pyqt installation
    - export PYTHONPATH=/usr/local/lib/python2.7/site-packages:$PYTHONPATH
  - creating standalone app
    - python pyinstaller/pyinstaller.py --onedir -w app.py

### On Windows (32-bit):
  - install python 2.7 from ActiveState distribution
  - install Qt binaries
  - install PyQt binaries
