import os
import re
import sys
import platform
import subprocess
from setuptools import setup, Extension
from setuptools.command.build_ext import build_ext

class CMakeExtension(Extension):
    def __init__(self, name, sourcedir=''):
        Extension.__init__(self, name, sources=[])
        self.sourcedir = os.path.abspath(sourcedir)

class CMakeBuild(build_ext):
    def run(self):
        try:
            subprocess.check_output(['cmake', '--version'])
        except OSError:
            raise RuntimeError("CMake must be installed to build CityFlow")

        for ext in self.extensions:
            self.build_extension(ext)

    def build_extension(self, ext):
        extdir = os.path.abspath(os.path.dirname(self.get_ext_fullpath(ext.name)))
        cmake_args = ['-DCMAKE_LIBRARY_OUTPUT_DIRECTORY=' + extdir,
                      '-DPYTHON_EXECUTABLE=' + sys.executable]

        cfg = 'Debug' if self.debug else 'Release'
        build_args = ['--config', cfg]

        # Fix for Python 3.12+ and modern compilers
        if platform.system() != "Windows":
            cmake_args += ['-DCMAKE_BUILD_TYPE=' + cfg]
            # Use all available cores for faster build
            build_args += ['--', '-j' + str(os.cpu_count() or 2)]
            # Add permissive flags to bypass Python 3.12 internal frame errors
            os.environ["CXXFLAGS"] = os.environ.get("CXXFLAGS", "") + " -fpermissive"
        
        if not os.path.exists(self.build_temp):
            os.makedirs(self.build_temp)
            
        subprocess.check_call(['cmake', ext.sourcedir] + cmake_args, cwd=self.build_temp)
        subprocess.check_call(['cmake', '--build', '.', '--target', 'cityflow'] + build_args, cwd=self.build_temp)

setup(
    name='CityFlow',
    version='0.1.1',
    author='Huichu Zhang',
    ext_modules=[CMakeExtension('cityflow')],
    cmdclass=dict(build_ext=CMakeBuild),
    zip_safe=False
)
