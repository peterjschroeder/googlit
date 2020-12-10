#!/usr/bin/env python3

from distutils.core import setup

setup(
        name='googlit', 
        version='0.1', 
        description='Frontend for googler', 
        author='Peter J. Schroeder', 
        author_email='peterjschroeder@gmail.com', 
        url='https://github.com/peterjschroeder/googlit',
        scripts=['googlit.py'],
        install_requires=['pyperclip', 'urwid']
)

