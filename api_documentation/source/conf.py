# Configuration file for the Sphinx documentation builder.
#
# For the full list of built-in configuration values, see the documentation:
# https://www.sphinx-doc.org/en/master/usage/configuration.html

# -- Project information -----------------------------------------------------
# https://www.sphinx-doc.org/en/master/usage/configuration.html#project-information
import sphinx_rtd_theme

project = 'nwb-photostim'
copyright = '2022'
author = 'sdsd'
release = '0.'

import os
import sys

sys.path.insert(0, os.path.abspath('../../src/pynwb'))
# sys.path.insert(0, os.path.abspath('../..'))

# -- Autodoc configuration -----------------------------------------------------

autoclass_content = 'both'
autodoc_docstring_signature = True
autodoc_member_order = 'bysource'

# -- General configuration ---------------------------------------------------
# https://www.sphinx-doc.org/en/master/usage/configuration.html#general-configuration

extensions = [
    'sphinx.ext.autodoc',
    'sphinx.ext.napoleon',
    'sphinx.ext.intersphinx',
    'sphinx.ext.viewcode',
    'sphinx.ext.extlinks',
    'sphinx_copybutton',
    'sphinx_rtd_theme'
]
templates_path = ['_templates']
exclude_patterns = []


html_theme = "sphinx_rtd_theme"