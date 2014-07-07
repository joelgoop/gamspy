# gamspy

Build and run GAMS models from python

## Aim of the project

I want to be able to create and run my GAMS models entirely from Python to avoid having to write GAMS code myself and to be able to manage all my data and other practicalities in Python.

So far, the project has only been tested for my own very specific needs and much functionality is probably missing. If you want something added, feel free to fork or add an issue!

## Documentation

There is currently no documentation other than this `README`, the example shown in the file [example.py](example.py), and the code itself.

## Installation

If you have the dependencies installed, you only need to `git clone` and compile the `cython` module `gdx_utils`. I have added the batch file ([cython.bat](cython.bat)) that I use on Windows 7 x64 for 64-bit Python, but you may have to adapt it to your own environment.

## Dependencies

In order to run the code you need the following packages (in addition to Python 2.7):
*   `jinja2` templating engine for writing the `GAMS` code
*   `numpy` for handling matrices 
*   `cython` to install the `gdx_utils` module, which efficiently parses data retrieved from `GDX` files
