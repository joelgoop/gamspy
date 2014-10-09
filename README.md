# gamspy

Build and run GAMS models from python.

Copyright (C) 2014 Joel Goop

## Aim of the project

I want to be able to create and run my GAMS models entirely from Python to avoid having to write GAMS code myself and to be able to manage all my data and other practicalities in Python.

So far, the project has only been tested for my own very specific needs and much functionality is probably missing. If you want something added, feel free to fork or add an issue!

## Documentation

There is currently no documentation other than this `README`, the example shown in the file [examples.py](gamspy/examples.py), and the code itself.

## Dependencies

Dependencies are listed in [setup.py](setup.py) and will be handled by `setuptools` or `pip`, but in order to compile the Cython module `gdx_utils` you need to install `numpy` first using `pip install` or any other method. 

You will also need the Python API package included with newer GAMS releases. If you haven't already, install GAMS. Then, in a command prompt, go to `<path to GAMS>/apifiles/Python/api` and run either `pip install .` or `python setup.py install`.

## Installation
For Windows 64-bit systems you can download a binary installer that can be used either directly or with `easy_install` (e.g. in a `virtualenv`). You can also install the package from source by downloading the source distributions from Releases or install directly from github using `pip install git+git://github.com/joelgoop/gamspy.git@<release-tag>#egg=gamspy`. (Since the github repository does not contain the `cython`-generated C code, this method will also require `cython` to compile the .pyx file to C code.) 

To install from source, you also need to have a correct build environment setup. I have tested the procedure on Ubuntu 14.04 64-bit and it seems to work well, but on Windows it can be a bit more tricky. I have installed Windows SDK and use the file [prepare_build_env.bat](prepare_build_env.bat) to set the correct environment variables, but there is no guarantee that this works anywhere else.  

## Licensing 

Copyright (C) 2014 Joel Goop
`gamspy` is licensed under the GNU General Public License version 3.

This program is free software: you can redistribute it and/or modify
it under the terms of the GNU General Public License as published by
the Free Software Foundation, either version 3 of the License, or
(at your option) any later version.

This program is distributed in the hope that it will be useful,
but WITHOUT ANY WARRANTY; without even the implied warranty of
MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE.  See the
GNU General Public License for more details.

You should have received a copy of the GNU General Public License
along with this program.  If not, see <http://www.gnu.org/licenses/>.