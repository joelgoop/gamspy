# gamspy

Build and run GAMS models from python.

Copyright (C) 2014 Joel Goop

## Aim of the project

I want to be able to create and run my GAMS models entirely from Python to avoid having to write GAMS code myself and to be able to manage all my data and other practicalities in Python.

So far, the project has only been tested for my own very specific needs and much functionality is probably missing. If you want something added, feel free to fork or add an issue!

## Documentation

There is currently no documentation other than this `README`, the example shown in the file [examples.py](examples.py), and the code itself.

## Dependencies

Dependencies are listed in [setup.py](setup.py) and will be handled by `setuptools`, but in order to compile the Cython module `gdx_utils` you need to install `numpy` first using `pip install` or any other method. 

You will also need the Python API package included with newer GAMS releases. If you haven't already, install GAMS. Then, in a command prompt, go to `<path to GAMS>/apifiles/Python/api` and run either `pip install .` or `python setup.py install`.

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