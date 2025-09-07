#!/usr/bin/env python3
"""
Setup script for Game Text Translator
Builds the C++ extension module using pybind11
"""

from setuptools import setup, Extension
from pybind11.setup_helpers import Pybind11Extension, build_ext
from pybind11 import get_cmake_dir
import pybind11
import sys
import os

# Define the C++ extension
ext_modules = [
    Pybind11Extension(
        "text_extractor",
        [
            "text_extractor.cpp",
        ],
        include_dirs=[
            # Path to pybind11 headers
            pybind11.get_include(),
        ],
        language='c++',
        cxx_std=17,
    ),
]

# Define the package
setup(
    name="game-text-translator",
    version="1.0.0",
    author="Game Translator Team",
    description="Fast text extraction and translation tool for game localization",
    long_description=open("README.md").read() if os.path.exists("README.md") else "",
    long_description_content_type="text/markdown",
    ext_modules=ext_modules,
    cmdclass={"build_ext": build_ext},
    zip_safe=False,
    python_requires=">=3.6",
    install_requires=[
        "pybind11>=2.6.0",
        "tkinter",  # Usually included with Python
    ],
    classifiers=[
        "Development Status :: 4 - Beta",
        "Intended Audience :: Developers",
        "License :: OSI Approved :: MIT License",
        "Programming Language :: Python :: 3",
        "Programming Language :: Python :: 3.6",
        "Programming Language :: Python :: 3.7",
        "Programming Language :: Python :: 3.8",
        "Programming Language :: Python :: 3.9",
        "Programming Language :: Python :: 3.10",
        "Programming Language :: Python :: 3.11",
        "Programming Language :: C++",
        "Topic :: Software Development :: Localization",
        "Topic :: Games/Entertainment",
    ],
    entry_points={
        "console_scripts": [
            "game-translator=game_translator:main",
        ],
    },
)
