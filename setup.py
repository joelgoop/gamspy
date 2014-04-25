from distutils.core import setup
from distutils.extension import Extension
from Cython.Distutils import build_ext
import numpy as np

ext_module = Extension(
    "gdx_utils",
    ["gdx_utils.pyx"],
    include_dirs = [np.get_include()]
)

setup(
    name = 'GDX utilities',
    cmdclass = {'build_ext': build_ext},
    ext_modules = [ext_module],
)