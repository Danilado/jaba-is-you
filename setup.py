from Cython.Build import cythonize
from setuptools import setup, Extension, find_packages

cython_directives = {
    'embedsignature': True,
    'language_level': "3",
    'linetrace': True,
    'binding': True
}

extensions = cythonize([
    Extension(name='jaba_speedup',
              sources=["jaba_speedup/*.pyx"]),
], compiler_directives=cython_directives)

setup(
    ext_modules=extensions
)
