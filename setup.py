#!/usr/bin/env python3
"""
Setup script for UDPsender
"""

from setuptools import setup, find_packages

setup(
    name="udpsender",
    version="1.0.0",
    description="A GUI application to send commands to any device over UDP",
    author="Chris Bovee",
    url="https://github.com/Chrismofer/UDPsender",
    packages=find_packages(),
    py_modules=['main', 'config'],
    install_requires=[
        # No external dependencies required
        # tkinter is included with Python
    ],
    python_requires='>=3.6',
    entry_points={
        'console_scripts': [
            'udpsender=main:main',
        ],
    },
    classifiers=[
        "Programming Language :: Python :: 3",
        "License :: OSI Approved :: MIT License",
        "Operating System :: OS Independent",
    ],
)
