# gamspy - Build and run GAMS models from Python
# Copyright (C) 2014 Joel Goop
#
# This program is free software: you can redistribute it and/or modify
# it under the terms of the GNU General Public License as published by
# the Free Software Foundation, either version 3 of the License, or
# (at your option) any later version.
#
# This program is distributed in the hope that it will be useful,
# but WITHOUT ANY WARRANTY; without even the implied warranty of
# MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE.  See the
# GNU General Public License for more details.
#
# You should have received a copy of the GNU General Public License
# along with this program.  If not, see <http://www.gnu.org/licenses/>.
#
from distutils.core import setup
from setuptools.command.test import test as TestCommand
from distutils.extension import Extension
from distutils.command.sdist import sdist as _sdist
import numpy as np
import gamspy
import os
import sys

cmdclass = {}
ext_modules = []

try:
    from Cython.Distutils import build_ext
except ImportError:
    use_cython = False
else:
    use_cython = True

class PyTest(TestCommand):
    def finalize_options(self):
        TestCommand.finalize_options(self)
        self.test_args = []
        self.test_suite = True

    def run_tests(self):
        import pytest
        errcode = pytest.main(["gamspy"]+self.test_args)
        sys.exit(errcode)

if use_cython:
    class sdist(_sdist):
        def run(self):
            # Make sure the compiled Cython files in the distribution are up-to-date
            from Cython.Build import cythonize
            print "Cythonizing..."
            cythonize(['gamspy/gdx_utils.pyx'])
            _sdist.run(self)
    cmdclass.update({'sdist': sdist})
    ext_modules += [Extension(
                        "gamspy.gdx_utils",
                        ["gamspy/gdx_utils.pyx"],
                        include_dirs = [np.get_include()]
                )]
    cmdclass.update({ 'build_ext': build_ext })
else:
    ext_modules += [Extension(
                        "gamspy.gdx_utils",
                        ["gamspy/gdx_utils.c"],
                        include_dirs = [np.get_include()]
                )]

cmdclass.update({'test': PyTest})

setup(
    name='gamspy',
    version=gamspy.__version__,
    url='http://github.com/joelgoop/gamspy',
    license='GNU General Public License v3 (GPLv3)',
    author='Joel Goop',
    tests_require=['pytest'],
    test_suite='gamspy.test',
    install_requires=['GAMS==1.0',
                        'MarkupSafe==0.23',
                        'cfgmcc==1',
                        'colorama==0.3.2',
                        'jinja2==2.7.3',
                        'numpy==1.9.0',
                        'py==1.4.25',
                        'pytest==2.6.3',
                    ],
    cmdclass=cmdclass,
    ext_modules = ext_modules,
    description='Build and run GAMS models from Python',
    packages=['gamspy'],
    package_data={
        'gamspy': ['templates/*.j2'],
    },
    include_package_data=True,
    platforms='any',
    classifiers = [
        'Development Status :: 4 - Beta',
        'Natural Language :: English',
        'License :: OSI Approved :: GNU General Public License v3 (GPLv3)',
        'Operating System :: OS Independent',
        ],
    extras_require={
        'testing': ['pytest'],
    }
)