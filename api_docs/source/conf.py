# Configuration file for the Sphinx documentation builder.
#
# For the full list of built-in configuration values, see the documentation:
# https://www.sphinx-doc.org/en/master/usage/configuration.html

# -- Project information -----------------------------------------------------
# https://www.sphinx-doc.org/en/master/usage/configuration.html#project-information
import sphinx_rtd_theme

project = 'nwb-photostim'
copyright = '2022'
author = 'Carl Harris'
version = '0.1.0'
release = 'alpha'

import os
import sys
import textwrap

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
    'sphinx.ext.ifconfig',
    'sphinx.ext.napoleon',
    'sphinx.ext.intersphinx',
    'sphinx.ext.viewcode',
    'sphinx.ext.extlinks',
    'sphinx_copybutton',
    'sphinx_rtd_theme'
]
templates_path = ['_templates']
exclude_patterns = []

latex_elements = {
        # The paper size ('letterpaper' or 'a4paper').
        'papersize': 'letterpaper',

        # The font size ('10pt', '11pt' or '12pt').
        'pointsize': '10pt',
    }

# -- Customize sphinx settings
numfig = True
add_function_parentheses = False

# -- HTML sphinx options
html_theme = "sphinx_rtd_theme"
html_theme_path = [sphinx_rtd_theme.get_html_theme_path()]
